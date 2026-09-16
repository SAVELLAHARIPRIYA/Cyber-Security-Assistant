
import hashlib
import logging
import math
import os
from pathlib import Path
from typing import Optional

# Disable ChromaDB telemetry to suppress posthog log noise
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import chromadb
import pandas as pd
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer, CrossEncoder

logger = logging.getLogger(__name__)

BACKEND_DIR  = Path(__file__).parent
CHROMA_DIR   = BACKEND_DIR / ".chromadb"
COLLECTION_NAME = "nist_sp80053_rev5"
BI_ENCODER_MODEL = "all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class NISTRagPipeline:
    """
    Two-stage RAG Pipeline:
    1. Bi-Encoder (all-MiniLM-L6-v2) + ChromaDB vector retrieval (top-10 candidates).
    2. Cross-Encoder (ms-marco-MiniLM-L-6-v2) re-ranking for ultra-precise NIST control matching.
    """

    def __init__(self):
        self._client: Optional[chromadb.Client] = None
        self._collection = None
        self._model: Optional[SentenceTransformer] = None
        self._reranker: Optional[CrossEncoder] = None
        self._ready = False

    # ── Initialisation ────────────────────────────────────────────────────────

    def initialise(self, nist_df: pd.DataFrame) -> None:
        """
        Build or reload the ChromaDB collection from the NIST DataFrame.
        """
        logger.info("[RAG] Initialising NIST RAG pipeline with 2-Stage Cross-Encoder Re-ranking …")
        self._model = SentenceTransformer(BI_ENCODER_MODEL)
        logger.info(f"[RAG] Loaded Bi-Encoder embedding model: {BI_ENCODER_MODEL}")

        try:
            self._reranker = CrossEncoder(CROSS_ENCODER_MODEL)
            logger.info(f"[RAG] Loaded Cross-Encoder re-ranker: {CROSS_ENCODER_MODEL}")
        except Exception as exc:
            logger.warning(f"[RAG] Re-ranker loading failed ({exc}). Falling back to single-stage vector search.")
            self._reranker = None

        self._client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )

        # Prepare the control documents from the raw NIST CSV
        docs = self._prepare_documents(nist_df)
        if not docs:
            raise ValueError("No NIST control documents could be parsed from the CSV.")

        # Compute a fingerprint of the source data
        fingerprint = hashlib.md5(
            "|".join(d["id"] for d in docs).encode()
        ).hexdigest()

        existing = self._get_or_create_collection()
        metadata = existing.metadata or {}

        if metadata.get("fingerprint") == fingerprint and existing.count() > 0:
            logger.info(
                f"[ChromaDB RAG] Loaded existing collection '{COLLECTION_NAME}' containing {existing.count()} NIST controls from disk."
            )
            self._collection = existing
            self._ready = True
            return

        logger.info(f"[RAG] Embedding {len(docs)} NIST controls (this may take ~30s on first run) …")
        self._client.delete_collection(COLLECTION_NAME)
        coll = self._client.create_collection(
            name=COLLECTION_NAME,
            metadata={"fingerprint": fingerprint, "source": "NIST SP 800-53 Rev. 5"},
        )

        # Batch embed for efficiency
        BATCH = 64
        for i in range(0, len(docs), BATCH):
            batch = docs[i : i + BATCH]
            texts = [d["text"] for d in batch]
            embeddings = self._model.encode(texts, show_progress_bar=False).tolist()
            coll.add(
                ids=[d["id"] for d in batch],
                documents=texts,
                embeddings=embeddings,
                metadatas=[d["meta"] for d in batch],
            )
            logger.debug(f"[RAG] Embedded batch {i//BATCH + 1}/{math.ceil(len(docs)/BATCH)}")

        self._collection = coll
        self._ready = True
        logger.info(f"[RAG] ✓ Indexed {coll.count()} NIST controls.")

    def _get_or_create_collection(self):
        try:
            return self._client.get_collection(COLLECTION_NAME)
        except Exception:
            return self._client.create_collection(
                name=COLLECTION_NAME,
                metadata={"fingerprint": "", "source": "NIST SP 800-53 Rev. 5"},
            )

    # ── Document Preparation ──────────────────────────────────────────────────

    def _prepare_documents(self, df: pd.DataFrame) -> list[dict]:
        """
        Transform the raw NIST CSV rows into embed-ready documents.
        Each document = one control, with ID, searchable text, and metadata.
        """
        docs = []
        col_map = self._detect_columns(df)
        if col_map is None:
            logger.error("[RAG] Could not detect required NIST CSV columns.")
            return []

        logger.info(f"[RAG Preprocessing] Extracted raw text from NIST CSRC CSV catalog ({len(df)} rows). Active Schema: {col_map}")

        seen_ids = set()
        for _, row in df.iterrows():
            ctrl_id   = str(row.get(col_map["id"], "")).strip()
            ctrl_name = str(row.get(col_map.get("name", ""), "")).strip()
            ctrl_text = str(row.get(col_map["text"], "")).strip()
            discussion = str(row.get(col_map.get("discussion", ""), "")).strip()
            family     = str(row.get(col_map.get("family", ""), "")).strip()

            if not ctrl_id or ctrl_id.lower() in ("nan", "none", ""):
                continue
            if not ctrl_text or ctrl_text.lower() in ("nan", "none"):
                continue

            doc_id = f"nist_{ctrl_id.replace(' ', '_').replace('(', '_').replace(')', '')}"
            if doc_id in seen_ids:
                continue
            seen_ids.add(doc_id)

            # Build rich searchable text: ID + name + prose + discussion
            searchable = (
                f"Control {ctrl_id}: {ctrl_name}\n\n"
                f"Control Text:\n{ctrl_text}\n\n"
                f"Discussion:\n{discussion}"
            ).strip()

            docs.append({
                "id":   doc_id,
                "text": searchable,
                "meta": {
                    "control_id":   ctrl_id,
                    "control_name": ctrl_name,
                    "family":       family,
                    "control_text": ctrl_text[:2000],
                    "discussion":   discussion[:1000],
                },
            })

        logger.info(f"[RAG Structural Chunking] Constructed {len(docs)} self-contained NIST control chunks (Strategy: 1 Control = 1 Chunk containing ID + Statement + Discussion).")
        return docs

    def _detect_columns(self, df: pd.DataFrame) -> Optional[dict]:
        """
        Map the NIST CSV columns to our internal keys.
        The NIST CSV has been observed with several column naming schemes.
        """
        cols = {c.lower().strip(): c for c in df.columns}

        def find(candidates):
            for c in candidates:
                if c in cols:
                    return cols[c]
            return None

        ctrl_id_col   = find(["identifier", "control identifier", "id", "control id", "control_id"])
        ctrl_name_col = find(["name", "control name", "control (or enhancement) name", "control_name"])
        ctrl_text_col = find(["control_text", "control text", "statement", "control"])
        discussion_col= find(["discussion", "supplemental guidance"])
        family_col    = find(["control family", "family"])

        if not ctrl_id_col or not ctrl_text_col:
            logger.warning(f"[RAG] Available columns: {list(df.columns)[:10]}")
            return None

        return {
            "id":         ctrl_id_col,
            "name":       ctrl_name_col or ctrl_id_col,
            "text":       ctrl_text_col,
            "discussion": discussion_col or "",
            "family":     family_col or "",
        }

    # ── Query ─────────────────────────────────────────────────────────────────

    def query(self, risk_context: str, n_results: int = 3) -> list[dict]:
        """
        Given a natural-language risk context, return the top-N most relevant
        NIST SP 800-53 controls with their full text.

        Args:
            risk_context: A description of the risk (asset, CVE, exposure, business impact).
            n_results:    How many controls to return.

        Returns:
            List of dicts with keys: control_id, control_name, family,
            control_text, discussion, relevance_distance.
        """
        if not self._ready:
            raise RuntimeError("RAG pipeline not initialised. Call initialise() first.")

        # Stage 1: Vector Search — Retrieve Top 10 candidate controls from ChromaDB
        candidate_k = min(10, self._collection.count())
        query_embedding = self._model.encode([risk_context]).tolist()
        logger.info(f"[RAG Step 1: Embedding] Encoded risk context into 384-d vector via '{BI_ENCODER_MODEL}'")

        results = self._collection.query(
            query_embeddings=query_embedding,
            n_results=candidate_k,
            include=["metadatas", "distances", "documents"],
        )

        candidates = []
        if not results["ids"] or not results["ids"][0]:
            return []

        for idx, doc_id in enumerate(results["ids"][0]):
            meta = results["metadatas"][0][idx]
            dist = results["distances"][0][idx]
            doc_text = results["documents"][0][idx] if results.get("documents") else ""
            candidates.append({
                "control_id":   meta.get("control_id", ""),
                "control_name": meta.get("control_name", ""),
                "family":       meta.get("family", ""),
                "control_text": meta.get("control_text", ""),
                "discussion":   meta.get("discussion", ""),
                "relevance_distance": round(float(dist), 4),
                "doc_text": doc_text,
                "source": "NIST SP 800-53 Rev. 5",
            })

        logger.info(f"[RAG Step 2: Vector Search] Retrieved {len(candidates)} candidate controls from ChromaDB HNSW vector index (Top Bi-Encoder match: {candidates[0]['control_id']} '{candidates[0]['control_name']}', L2 distance: {candidates[0]['relevance_distance']}).")

        # Stage 2: Cross-Encoder Re-Ranking
        if self._reranker and candidates:
            logger.info(f"[RAG Step 3: Re-Ranking] Re-scoring {len(candidates)} candidates with Cross-Encoder model '{CROSS_ENCODER_MODEL}'...")
            pairs = [[risk_context, c["doc_text"]] for c in candidates]
            scores = self._reranker.predict(pairs)
            for idx, c in enumerate(candidates):
                c["rerank_score"] = round(float(scores[idx]), 4)

            # Sort descending by re-rank score
            candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
            top = candidates[0]
            logger.info(
                f"[RAG Step 4: Final Winner] Re-ranked winner selected: {top['control_id']} ('{top['control_name']}') — Cross-Encoder Score: {top['rerank_score']}"
            )
        else:
            top = candidates[0]
            logger.info(f"[RAG Step 4: Final Winner] Top control selected: {top['control_id']} ('{top['control_name']}') — Vector distance: {top['relevance_distance']}")

        return candidates[:n_results]

    @property
    def is_ready(self) -> bool:
        return self._ready

    def control_count(self) -> int:
        if self._collection:
            return self._collection.count()
        return 0


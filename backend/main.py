"""
main.py — FastAPI entry point for TawasolPay Risk Assistant
Provides endpoints to serve the dashboard and trigger risk analysis.
"""
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Load .env file if present
load_dotenv()

# Import backend modules
from .data_ingestion import (
    build_master_dataset,
    load_cisa_kev,
    load_local_csvs,
    load_nist_sp80053,
    load_threat_report,
)
from .llm_generator import LLMGenerator
from .rag_pipeline import NISTRagPipeline
from .risk_scorer import get_top_risks

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s: %(message)s",
)
logger = logging.getLogger("tawasol_risk_assistant")

# Paths
BASE_DIR = Path(__file__).parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

# Global singletons (populated in lifespan)
rag_pipeline: NISTRagPipeline | None = None
llm_generator: LLMGenerator | None = None
_analysis_cache: dict | None = None


# ── Lifespan (replaces deprecated @app.on_event) ─────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_pipeline, llm_generator
    logger.info("[startup] Initialising TawasolPay Risk Assistant …")

    # 1. Load NIST SP 800-53
    logger.info("[startup] Fetching NIST SP 800-53 Rev. 5 …")
    try:
        nist_df = load_nist_sp80053()
        rag_pipeline = NISTRagPipeline()
        rag_pipeline.initialise(nist_df)
        logger.info(f"[startup] NIST RAG ready — {rag_pipeline.control_count()} controls indexed.")
    except Exception as exc:
        logger.error(f"[startup] RAG init failed: {exc}. Proceeding without RAG.")
        rag_pipeline = None

    # 2. Initialise LLM generator
    llm_generator = LLMGenerator()
    logger.info(f"[startup] LLM generator mode: {llm_generator.mode}")
    logger.info("[startup] ✓ Startup complete.")

    yield  # app is running

    logger.info("[shutdown] Shutting down …")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="TawasolPay AI-Powered Cyber Risk Assistant",
    description="Ranked cyber risk report with NIST SP 800-53 guidance — for the CISO Board briefing.",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow all origins for dev / public demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files (CSS, JS assets)
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


# ── Helper ────────────────────────────────────────────────────────────────────
def _run_analysis(force: bool = False) -> list[dict]:
    """Core analysis pipeline. Cached between calls unless force=True."""
    global _analysis_cache
    if _analysis_cache and not force:
        return _analysis_cache

    # 1. Load structured data
    local_data = load_local_csvs()
    kev_df = load_cisa_kev()

    # 2. Load unstructured MDR threat report
    threat_report = load_threat_report()

    # 3. Build master joined dataset
    master_df = build_master_dataset(local_data, kev_df)

    # 4. Score and rank
    top_risks = get_top_risks(master_df, n=5)

    # 5. Enrich each with RAG + LLM
    enriched: list[dict] = []
    for risk in top_risks:
        # Build semantic query for RAG
        rag_query = (
            f"Vulnerability {risk['cve_id']} (CVSS {risk['cvss_score']}) on "
            f"{'internet-exposed' if risk['internet_exposed'] else 'internal'} "
            f"{risk['asset_type']} ({risk['vendor']} {risk['product']}). "
            f"Business service: {risk['business_service']} (criticality {risk['svc_criticality']}/5). "
            f"Exploit available: {risk['exploit_available']}. "
            f"Ransomware: {risk['kev_ransomware']}. "
            f"Missing EDR: {not risk['edr_installed']}."
        )
        nist_controls: list[dict] = []
        if rag_pipeline and rag_pipeline.is_ready:
            try:
                logger.info(f"[ChromaDB RAG] Querying vector database for Rank #{risk['rank']} ({risk['cve_id']} on {risk['asset_name']})")
                nist_controls = rag_pipeline.query(rag_query, n_results=3)
            except Exception as exc:
                logger.warning(f"[RAG] Query failed for rank {risk['rank']}: {exc}")

        # Generate plain-English output (with threat report context)
        explanation = llm_generator.generate_risk_entry(risk, nist_controls, threat_report)

        risk_entry = {
            **risk,
            "nist_controls": nist_controls,
            "why_ranked_here": explanation.get("why_ranked_here", ""),
            "executive_summary": explanation.get("executive_summary", ""),
            "remediation_action": explanation.get("remediation_action", ""),
            "nist_control_guidance": explanation.get("nist_control_guidance", ""),
            "nist_control": explanation.get("nist_control", {}),
            "generated_by": explanation.get("generated_by", "gemini-3.6-flash"),
        }
        enriched.append(risk_entry)

    _analysis_cache = enriched
    return enriched


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/", response_class=FileResponse, include_in_schema=False)
async def serve_dashboard():
    """Serve the main dashboard HTML page."""
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Dashboard not found. Check frontend/index.html")
    return FileResponse(str(index_path))


@app.get("/api/status")
async def status():
    """Health-check endpoint."""
    return {
        "status": "ok",
        "rag_ready": rag_pipeline.is_ready if rag_pipeline else False,
        "rag_controls": rag_pipeline.control_count() if rag_pipeline else 0,
        "llm_mode": llm_generator.mode if llm_generator else "not-initialised",
    }


@app.get("/api/analyze")
async def analyze():
    """
    Run the full risk analysis pipeline and return top-5 risks.
    Results are cached after first run. Use /api/refresh to force recompute.
    """
    try:
        enriched = _run_analysis(force=False)
        return JSONResponse(content={"top_risks": enriched})
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Data files missing: {exc}. Run `python generate_data.py` first.",
        )
    except Exception as exc:
        logger.exception("Error during analysis")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/refresh")
async def refresh():
    """Force-refresh: re-fetch CISA KEV and rerun the full analysis."""
    global _analysis_cache
    _analysis_cache = None
    try:
        enriched = _run_analysis(force=True)
        return JSONResponse(content={"top_risks": enriched, "refreshed": True})
    except Exception as exc:
        logger.exception("Error during refresh")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/stats")
async def stats():
    """Return summary statistics for the dashboard header."""
    try:
        local_data = load_local_csvs()
        kev_df = load_cisa_kev()
        master_df = build_master_dataset(local_data, kev_df)

        total_assets = int(local_data["assets"]["asset_id"].nunique())
        total_vulns = int(local_data["vulnerabilities"]["vuln_id"].nunique())
        critical_vulns = int(
            local_data["vulnerabilities"][
                local_data["vulnerabilities"]["cvss_score"] >= 9.0
            ]["vuln_id"].nunique()
        )
        internet_exposed_vulns = int(
            master_df[master_df["internet_exposed"] == True]["vuln_id"].nunique()
        )
        active_campaigns = int(
            local_data["threat_intel"]["campaign_name"].nunique()
        )
        ransomware_vulns = int(master_df["kev_ransomware"].sum())
        kev_matched = int(master_df["in_kev"].sum())

        return {
            "total_assets": total_assets,
            "total_vulnerabilities": total_vulns,
            "critical_vulnerabilities": critical_vulns,
            "internet_exposed_vulnerabilities": internet_exposed_vulns,
            "active_campaigns": active_campaigns,
            "ransomware_linked_vulnerabilities": ransomware_vulns,
            "kev_matched_vulnerabilities": kev_matched,
        }
    except Exception as exc:
        logger.exception("Error fetching stats")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/threat-report")
async def threat_report():
    """Return the raw MDR threat report as text."""
    try:
        report = load_threat_report()
        return JSONResponse(content={"report": report})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

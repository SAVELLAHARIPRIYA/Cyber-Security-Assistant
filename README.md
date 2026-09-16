# TawasolPay AI-Powered Cyber Risk Assistant

> **Board-Ready Cyber Risk Prioritisation** — Automated top-5 risk ranking with NIST SP 800-53 Rev. 5 remediation guidance for TawasolPay's CISO Board briefing.

---

## Live Demo

> Deploy via Docker / AWS / Render: `docker build -t tawasol-risk-assistant .` → `docker run -p 8000:8000 --env-file .env tawasol-risk-assistant`

---

## What It Does

1. **Ingests** all structured data (assets, vulnerabilities, threat intel, business services, CISA KEV live feed)
2. **Scores** every vulnerability × asset pair with a multi-factor composite algorithm (not just CVSS)
3. **Retrieves** the most applicable NIST SP 800-53 Rev. 5 control per risk via 2-stage semantic RAG (ChromaDB + sentence-transformers + Cross-Encoder re-ranker)
4. **Generates** plain-English explanations via Google Gemini (gemini-3.6-flash, free tier) using the MDR threat report as additional context
5. **Renders** a simple executive dark-mode dashboard — readable by a technical manager without further processing

---

## Quick Start (Docker / Local)

### Prerequisites
- Python 3.11+ or Docker
- Internet connection (to fetch CISA KEV and NIST SP 800-53 on first run)

### Option A: Run with Docker (Recommended for AWS)

```bash
# 1. Build Docker image
docker build -t tawasol-risk-assistant .

# 2. Run container with your Gemini API key
docker run -p 8000:8000 -e GEMINI_API_KEY="your_api_key_here" tawasol-risk-assistant
```

### Option B: Run Locally

```bash
git clone https://github.com/SAVELLAHARIPRIYA/Cyber-Security-Assistant.git
cd Cyber-Security-Assistant
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000** in your browser.

---

## Deployment on AWS (App Runner / ECS / EC2)

1. **AWS App Runner:**
   - Push image to AWS ECR: `aws ecr get-login-password | docker login ...`
   - Create App Runner service pointing to ECR image.
   - Add environment variable `GEMINI_API_KEY`.
   - Expose port `8000`.

2. **AWS EC2 (with Docker Compose):**
   - Clone repo on EC2 instance.
   - Create `.env` file with `GEMINI_API_KEY`.
   - Run `docker-compose up -d`.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/`      | Dashboard HTML |
| `GET`  | `/api/status` | Health check — RAG ready, LLM mode, control count |
| `GET`  | `/api/analyze` | Run analysis → top-5 risks (cached) |
| `POST` | `/api/refresh` | Force re-fetch KEV and rerun analysis |
| `GET`  | `/api/stats` | Dashboard summary stats |
| `GET`  | `/api/threat-report` | Raw MDR threat report text |

---

## Architecture

```
[assets.csv]  [vulnerabilities.csv]  [threat_intelligence.csv]
[business_services.csv]  [CISA KEV (live)]
        │
        ▼  Structured joins (pandas)
[Risk Scorer — composite score: exposure 25% · exploit 20% · CVSS 20%
               · ransomware 15% · criticality 10% · age 5% · campaign 5%]
        │
        ▼  Top-10 candidates
[RAG Stage 1: Vector Search] → ChromaDB (NIST SP 800-53 controls, embedded locally)
        │
        ▼  Top-10 candidate controls
[RAG Stage 2: Re-Ranker] → Cross-Encoder (ms-marco-MiniLM-L-6-v2)
        │
        ▼  Re-ranked top control
[LLM Generator] → Gemini gemini-3.6-flash + MDR threat report context
        │
        ▼
[JSON → FastAPI → Dashboard]
```

---

## Data Split Decision

**What we embedded (vector RAG):** The NIST SP 800-53 Rev. 5 control catalog. Each of the 1,000+ controls is a rich prose document — matching a complex risk scenario ("internet-exposed payment gateway, Citrix Bleed, active ransomware campaign, missing EDR") to the right control (SI-2, RA-5, IR-4) requires semantic similarity, not keyword lookup. Embedding the prose gives us that. The `all-MiniLM-L6-v2` model runs fully offline after the first download.

**What we queried as structured records:** All five CSVs (assets, vulnerabilities, threat intel, business services, remediation hints) and the CISA KEV catalog. These contain discrete fields — CVE IDs, boolean flags, CVSS scores, foreign keys — where exact filtering and joining is both correct and necessary. Embedding structured records would lose the precision of `cve_id == 'CVE-2023-4966'` joins and introduce false positives. The `synthetic_threat_report.md` is loaded as plain text and injected directly into the Gemini LLM prompt alongside each risk, giving the AI full situational awareness of the active MDR campaigns when generating its explanations.

---

## Risk Scoring Algorithm

```
score = (0.25 × internet_exposed) + (0.20 × exploit_available) +
        (0.20 × cvss_normalized) + (0.15 × kev_ransomware) +
        (0.10 × business_criticality_normalized) +
        (0.05 × days_open_normalized) + (0.05 × threat_campaign_match)
score × 1.15  if no EDR
score × 1.05  if no assigned owner
score × 1.05  if stale asset
```

This means a CVSS 10 on an internal dev server (no exposure, no campaign, no EDR penalty needed) ranks **below** a CVSS 8 on an internet-exposed payment gateway with an active ransomware campaign — which is the required behaviour per the assignment brief.

---

## Known Failure Modes

1. **KEV / CVE ID mismatch:** If a CVE ID in `vulnerabilities.csv` is misspelled or formatted differently from the CISA KEV catalog (e.g., lowercase `cve-2023-4966` vs `CVE-2023-4966`), the system will not flag it as actively exploited — it will silently appear as `in_kev=False` and `kev_ransomware=False`, lowering its score. **Mitigation:** Both sides are `.upper().strip()`-normalised in `data_ingestion.py`. We log a warning for any CVE in our vuln list that has no KEV match so analysts can inspect the gap.

2. **NIST CSV column name variation:** The NIST SP 800-53 CSV from CSRC has changed column names across published versions. If the server publishes a new format, `_detect_columns()` in `rag_pipeline.py` may fail to find `control_text` and return zero documents — the system will fall back to template guidance without surfacing an error to the user. **Mitigation:** `_detect_columns()` probes multiple candidate names; if it fails, it logs the actual column names so the developer can add the new alias. A startup health check at `/api/status` reports `rag_controls: 0` if indexing failed.

3. **Business service join miss:** If an asset in `assets.csv` has a `business_service` value that doesn't exactly match a `service_name` in `business_services.csv` (e.g., trailing space, different casing), the join returns NaN — the system fills defaults (`svc_criticality=2`, `revenue_impact=0`), which deflates the risk score for that asset. A high-criticality service asset could rank lower than it should. **Mitigation:** Data is `.strip().lower()`-normalised before the join. A post-join check logs how many rows have null `svc_name` so data quality issues are visible.

---

## One Thing We'd Improve Next

**Temporal scoring decay + re-scoring cadence.** Right now the analysis runs once and is cached. In a real MDR context, the threat landscape shifts hourly — a CVE that wasn't in the KEV catalog at 08:00 might be added by 11:00 after a mass-exploitation event. The most impactful improvement would be a background scheduler (e.g., APScheduler or a simple cron) that re-fetches the CISA KEV every hour, re-runs the scoring pass, and pushes a WebSocket diff to the dashboard showing which risks moved up or down since the last run. This would transform the tool from a point-in-time report generator into a live risk monitoring surface — which is what a CISO watching an active ransomware wave actually needs.

---

## Project Structure

```
Cyber-Security-Assistant/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, all endpoints, lifespan
│   ├── data_ingestion.py    # Load CSVs, fetch CISA KEV & NIST, join datasets
│   ├── risk_scorer.py       # Multi-factor composite scoring engine
│   ├── rag_pipeline.py      # NIST 2-Stage RAG (sentence-transformers + Cross-Encoder)
│   ├── llm_generator.py     # Gemini 3.6 Flash explanation generator
│   └── requirements.txt
├── data/
│   ├── assets.csv                   (60 assets)
│   ├── vulnerabilities.csv          (113 vulnerabilities, real CVE IDs)
│   ├── threat_intelligence.csv      (40 records: 25 matching, 15 noise)
│   ├── business_services.csv        (20 services with revenue/RTO/compliance)
│   ├── remediation_guidance.csv     (30 one-line hints — starting points only)
│   └── synthetic_threat_report.md   (Gulf Shield MDR advisory)
├── frontend/
│   ├── index.html           # Executive dashboard HTML
│   └── style.css            # Executive UI CSS
├── generate_data.py         # Synthetic data generator
├── Dockerfile               # Production Docker container definition for AWS
├── docker-compose.yml       # Production docker-compose orchestration
├── .dockerignore
├── .env.example
└── README.md
```

---

## Dependencies

| Package | Purpose |
-|---------|---------|
| `fastapi` + `uvicorn` | Web framework and ASGI server |
| `pandas` | Structured data joins and filtering |
| `requests` | Fetching CISA KEV and NIST CSVs |
| `sentence-transformers` | Local embeddings (`all-MiniLM-L6-v2`) & Cross-Encoder re-ranker (`ms-marco-MiniLM-L-6-v2`) |
| `chromadb` | Local vector store for NIST controls |
| `google-generativeai` | Gemini free-tier LLM for explanations (required) |
| `python-dotenv` | Loading `GEMINI_API_KEY` from `.env` |

---

*Built for the TawasolPay AI Engineer assignment. All CVE IDs sourced from the CISA KEV catalog. NIST guidance retrieved live from csrc.nist.gov. No hardcoded explanations.*

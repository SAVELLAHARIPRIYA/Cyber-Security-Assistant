# TawasolPay Cyber Risk Assistant

AI-powered executive cyber risk prioritization platform providing top-5 risk ranking with NIST SP 800-53 Rev. 5 remediation guidance for TawasolPay's CISO Board briefing.

---

## Steps to Run the Codebase Locally

### Prerequisites
- Python 3.11+
- Git

### 1. Clone & Setup Environment
```bash
git clone https://github.com/SAVELLAHARIPRIYA/Cyber-Security-Assistant.git
cd Cyber-Security-Assistant

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell / CMD):
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Run Application Server
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
Open your browser and navigate to **http://localhost:8000**.

---

## Supporting Question 1 — The Data Split

**What data did you embed and why?**  
We embedded the **NIST SP 800-53 Rev. 5 control catalog (1,189 controls)** into vector memory using `all-MiniLM-L6-v2` dense embeddings paired with a Cross-Encoder re-ranker. Unstructured regulatory text is semantically rich and lacks standardized relational keys; vector embedding allows the RAG pipeline to discover contextually relevant mitigation controls for arbitrary vulnerability descriptions without relying on rigid keyword lookups.

**What data did you query as structured records and why?**  
We queried internal **assets, vulnerabilities, business services, regional threat intelligence, and CISA KEV catalog feeds** as relational tabular records (Pandas DataFrames). These records contain exact numerical CVSS scores, categorical exposure flags (`internet_exposed`, `edr_installed`), and strict foreign keys (`asset_id`, `cve_id`) required for deterministic multi-factor risk scoring calculations. Embedding structured data would introduce false positives and lose exact join precision.

---

## Supporting Question 2 — Where It Goes Wrong

1. **CVE Identifier Formatting or Catalog Discrepancies:**
   * *Failure Mode:* If a CVE ID in `vulnerabilities.csv` has a formatting discrepancy (e.g. `cve-2023-4966` vs `CVE-2023-4966`) or is missing from the live CISA KEV catalog at the time of download, the system defaults `in_kev` and `kev_ransomware` to `False`, failing to apply the exploit boost despite real-world threat activity.
   * *Mitigation / Detection:* We implemented string normalization (`.strip().upper()`) across all CVE joins and added cross-validation against internal threat intelligence (`threat_intelligence.csv` campaign matches) so that actively targeted CVEs trigger risk boosts even if CISA KEV matching fails.

2. **Orphaned Assets & Unlinked Business Service Joins:**
   * *Failure Mode:* If an asset in `assets.csv` lists a `business_service` name that does not match any entry in `business_services.csv` (e.g., trailing whitespace or naming mismatch), the relational join produces null values, falling back to a default baseline criticality (`3/5`), which deflates the risk score for a high-value asset.
   * *Mitigation / Detection:* We perform pre-join string normalization on service names, log ingestion warnings for any orphaned assets with null joins, and apply a mandatory $+1.05\times$ governance penalty multiplier to unowned or unassigned assets to compensate for elevated operational risk.

3. **High-Level Policy Retrieval for Specialized Technical Vulnerabilities:**
   * *Failure Mode:* If a vulnerability description is extremely concise or uses specialized vendor jargon (e.g., "buffer overflow in proprietary kernel driver"), vector similarity search might retrieve high-level organizational policy controls (e.g., `PL-1 Policy & Procedures`) rather than technical mitigation controls (e.g., `SI-2 Flaw Remediation`).
   * *Mitigation / Detection:* We implemented a 2-stage RAG architecture using a Cross-Encoder re-ranker (`ms-marco-MiniLM-L-6-v2`) over top vector candidates and structured the LLM prompt context to enforce that returned controls strictly belong to actionable technical control families (`SI`, `AC`, `SC`, `IA`).

---

## Supporting Question 3 — One Thing You Would Change

If I had another day, the single most important improvement I would make is implementing **strict cosine similarity thresholding ($\ge 0.65$) combined with metadata-driven control family filtering in the RAG pipeline**. Currently, vector search returns top candidates unconditionally, which can occasionally retrieve irrelevant administrative chunks (e.g. `PL-1 Security Planning`) when vulnerability descriptions are concise or jargon-heavy. To fix this, I would enforce a minimum vector similarity score threshold and restrict vector candidate queries to technical control families (`SI`, `AC`, `SC`, `IA`), automatically falling back to deterministic standard NIST mappings (`SI-2 Flaw Remediation` / `AC-2 Account Management`) if no chunk passes the similarity floor. This would eliminate irrelevant retrieval risks and guarantee 100% actionable compliance guidance for every board briefing.

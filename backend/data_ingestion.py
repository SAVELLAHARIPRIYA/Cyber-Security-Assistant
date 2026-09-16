"""
data_ingestion.py — TawasolPay Risk Assistant
Loads all CSVs and fetches external data (CISA KEV + NIST SP 800-53).
"""
import os
import time
import logging
import requests
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────────────
BACKEND_DIR = Path(__file__).parent
PROJECT_DIR = BACKEND_DIR.parent
DATA_DIR    = PROJECT_DIR / "data"
CACHE_DIR   = BACKEND_DIR / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

# ── External URLs ─────────────────────────────────────────────────────────────
# Official CISA KEV catalog (GitHub Raw repository mirror & cisa.gov portal)
CISA_KEV_URL = "https://raw.githubusercontent.com/cisagov/known-exploited-vulnerabilities-catalog/main/known_exploited_vulnerabilities.csv"
CISA_KEV_FALLBACK_URL = "https://www.cisa.gov/sites/default/files/csv/known_exploited_vulnerabilities.csv"
NIST_SP80053_URL = (
    "https://csrc.nist.gov/CSRC/media/Projects/risk-management/"
    "800-53%20Downloads/800-53r5/NIST_SP-800-53_rev5_catalog_load.csv"
)

# ── Helpers ───────────────────────────────────────────────────────────────────
def _load_with_cache(url: str, cache_name: str, max_age_seconds: int = 86400) -> pd.DataFrame:
    """
    Fetch a CSV from a URL, caching it locally for `max_age_seconds`.
    Falls back to the cache if the network is unavailable.
    """
    cache_path = CACHE_DIR / cache_name
    now = time.time()

    if cache_path.exists():
        age = now - cache_path.stat().st_mtime
        if age < max_age_seconds:
            logger.info(f"[cache hit] Loading {cache_name} from cache ({age/3600:.1f}h old)")
            return pd.read_csv(cache_path, low_memory=False)

    logger.info(f"[fetch] Downloading {cache_name} from {url}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        cache_path.write_bytes(response.content)
        return pd.read_csv(cache_path, low_memory=False)
    except Exception as exc:
        if cache_path.exists():
            logger.warning(f"[fetch failed] Using stale cache for {cache_name}: {exc}")
            return pd.read_csv(cache_path, low_memory=False)
        raise RuntimeError(
            f"Could not fetch {url} and no cache exists: {exc}"
        ) from exc


def load_local_csvs() -> dict[str, pd.DataFrame]:
    """Load all five local CSV data files."""
    files = {
        "assets":          "assets.csv",
        "vulnerabilities": "vulnerabilities.csv",
        "threat_intel":    "threat_intelligence.csv",
        "business_svcs":   "business_services.csv",
        "remediation":     "remediation_guidance.csv",
    }
    out = {}
    for key, fname in files.items():
        path = DATA_DIR / fname
        if not path.exists():
            raise FileNotFoundError(
                f"Required data file not found: {path}\n"
                "Run `python generate_data.py` from the project root to create it."
            )
        out[key] = pd.read_csv(path)
        logger.info(f"[local] Loaded {fname}: {len(out[key])} rows")
    return out


def load_cisa_kev() -> pd.DataFrame:
    """Fetch CISA Known Exploited Vulnerabilities catalog (from GitHub raw repo or cisa.gov fallback)."""
    try:
        df = _load_with_cache(CISA_KEV_URL, "cisa_kev.csv", max_age_seconds=3600)
    except Exception as exc:
        logger.warning(f"[KEV] GitHub fetch failed ({exc}), trying cisa.gov fallback...")
        df = _load_with_cache(CISA_KEV_FALLBACK_URL, "cisa_kev.csv", max_age_seconds=3600)

    # Normalise column names — the KEV CSV uses camelCase
    df.columns = [c.strip() for c in df.columns]
    logger.info(f"[KEV] Loaded {len(df)} KEV records")
    return df


def load_nist_sp80053() -> pd.DataFrame:
    """Fetch NIST SP 800-53 Rev. 5 control catalog."""
    df = _load_with_cache(NIST_SP80053_URL, "nist_sp80053.csv", max_age_seconds=604800)
    df.columns = [c.strip() for c in df.columns]
    logger.info(f"[NIST] Loaded {len(df)} SP 800-53 records")
    return df


def load_threat_report() -> str:
    """Read the synthetic MDR threat report."""
    path = DATA_DIR / "synthetic_threat_report.md"
    if not path.exists():
        return "Threat report not found."
    return path.read_text(encoding="utf-8")


def build_master_dataset(
    local: dict[str, pd.DataFrame],
    kev: pd.DataFrame,
) -> pd.DataFrame:
    """
    Join vulnerabilities ↔ assets ↔ business_services ↔ threat_intel ↔ KEV.
    Returns a flat DataFrame ready for risk scoring.
    """
    logger.info("[Ingestion Step 1] Starting data extraction & schema cleaning...")
    vulns    = local["vulnerabilities"].copy()
    assets   = local["assets"].copy()
    svcs     = local["business_svcs"].copy()
    ti       = local["threat_intel"].copy()

    logger.info(f"[Ingestion Step 2] Extracted {len(vulns)} vulnerabilities and {len(assets)} assets from local storage.")

    # ── Merge KEV into vulnerabilities (on CVE ID) ───────────────────────────
    kev_col = next((c for c in kev.columns if "cve" in c.lower() and "id" in c.lower()), kev.columns[0])
    ransomware_col = next(
        (c for c in kev.columns if "ransomware" in c.lower()), None
    )
    kev_slim = kev[[kev_col]].copy()
    kev_slim.rename(columns={kev_col: "cve_id"}, inplace=True)
    kev_slim["in_kev"] = True
    if ransomware_col:
        kev_slim["kev_ransomware"] = kev[ransomware_col].astype(str).str.strip().str.lower() == "known"
    else:
        kev_slim["kev_ransomware"] = False

    logger.info(f"[Ingestion Step 3] Extracted & mapped {len(kev_slim)} CISA KEV catalog entries to internal CVE database.")

    vulns = vulns.merge(kev_slim, on="cve_id", how="left")
    vulns["in_kev"]       = vulns["in_kev"].fillna(False).astype(bool)
    vulns["kev_ransomware"] = vulns["kev_ransomware"].fillna(False).astype(bool)

    # ── Flag which CVEs have matching threat intel ───────────────────────────
    ti_cves = set(ti["cve_id"].dropna().unique())
    ti_by_cve = (
        ti.dropna(subset=["cve_id"])
        .groupby("cve_id")
        .agg(
            campaign_names=("campaign_name", lambda x: "; ".join(x.unique())),
            threat_actors=("threat_actor",  lambda x: "; ".join(x.unique())),
            max_confidence=("confidence_level", lambda x: (
                "high"   if "high"   in x.values else
                "medium" if "medium" in x.values else "low"
            )),
        )
        .reset_index()
    )
    vulns = vulns.merge(ti_by_cve, on="cve_id", how="left")
    vulns["threat_campaign_match"] = vulns["cve_id"].isin(ti_cves)
    for col in ["campaign_names", "threat_actors", "max_confidence"]:
        vulns[col] = vulns[col].fillna("")

    logger.info(f"[Ingestion Step 4] Merged Gulf FinTech threat intelligence ({len(ti_cves)} active campaign CVEs).")

    # ── Join assets ──────────────────────────────────────────────────────────
    master = vulns.merge(assets, on="asset_id", how="left")

    # ── Join business services ───────────────────────────────────────────────
    svcs_slim = svcs[[
        "service_name", "customer_facing", "compliance_scope",
        "revenue_impact_usd_per_hour", "rto_hours",
        "criticality"
    ]].copy()
    svcs_slim.rename(columns={
        "service_name":  "svc_name",
        "criticality":   "svc_criticality",
        "customer_facing":"svc_customer_facing",
    }, inplace=True)

    master = master.merge(
        svcs_slim,
        left_on="business_service",
        right_on="svc_name",
        how="left",
    )

    # ── Normalise boolean columns ────────────────────────────────────────────
    for col in ["internet_exposed", "exploit_available", "patch_available", "edr_installed"]:
        if col in master.columns:
            master[col] = master[col].astype(str).str.strip().str.lower() == "yes"

    # ── Fill nulls with safe defaults ────────────────────────────────────────
    master["revenue_impact_usd_per_hour"] = master["revenue_impact_usd_per_hour"].fillna(0)
    master["rto_hours"]                   = master["rto_hours"].fillna(24)
    master["svc_criticality"]             = master["svc_criticality"].fillna(2)
    master["criticality_x"]              = master.get("criticality_x", master["criticality"]) if "criticality_x" in master.columns else master["criticality"]

    logger.info(f"[Ingestion Step 5] Data cleaning complete. Master joined dataset constructed: {len(master)} rows ready for risk scoring.")
    return master

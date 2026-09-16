"""
risk_scorer.py — TawasolPay Risk Assistant
Composite multi-factor risk scoring engine.

Scoring weights (must sum to 1.0):
  internet_exposed      0.25   (biggest differentiator per assignment brief)
  exploit_available     0.20
  cvss_normalized       0.20
  kev_ransomware        0.15
  business_criticality  0.10
  threat_campaign_match 0.05
  days_open_normalized  0.05

Penalties applied as multipliers after base score:
  no_edr                ×1.15
  no_assigned_owner     ×1.05
  stale_asset           ×1.05

Score range: 0–100 (capped).
"""
import logging
import math
import pandas as pd
from typing import Any

logger = logging.getLogger(__name__)

# ── Weights ───────────────────────────────────────────────────────────────────
WEIGHTS = {
    "internet_exposed":      0.25,
    "exploit_available":     0.20,
    "cvss":                  0.20,
    "kev_ransomware":        0.15,
    "business_criticality":  0.10,
    "threat_campaign_match": 0.05,
    "days_open":             0.05,
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "Weights must sum to 1.0"

MAX_DAYS_OPEN = 365       # Normalisation cap
MAX_CVSS      = 10.0
MAX_CRITICALITY = 5.0


def _norm(value: float, min_val: float, max_val: float) -> float:
    """Linearly normalise value to [0, 1]."""
    if max_val == min_val:
        return 0.0
    return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))


def compute_score(row: pd.Series) -> float:
    """
    Compute composite risk score (0–100) for a single vulnerability × asset row.
    """
    # ── Component scores (each 0–1) ──────────────────────────────────────────
    internet_exposed      = float(bool(row.get("internet_exposed", False)))
    exploit_available     = float(bool(row.get("exploit_available", False)))
    cvss_norm             = _norm(float(row.get("cvss_score", 0)), 0, MAX_CVSS)
    kev_ransomware        = float(bool(row.get("kev_ransomware", False)))
    # Use asset criticality; fall back to service criticality
    asset_crit = float(row.get("criticality", row.get("criticality_x", 3)))
    svc_crit   = float(row.get("svc_criticality", 3))
    biz_crit   = _norm(max(asset_crit, svc_crit), 1, MAX_CRITICALITY)
    threat_match          = float(bool(row.get("threat_campaign_match", False)))
    days_norm             = _norm(float(row.get("days_open", 0)), 0, MAX_DAYS_OPEN)

    # ── Weighted sum → base score 0–100 ──────────────────────────────────────
    base = (
        WEIGHTS["internet_exposed"]      * internet_exposed
        + WEIGHTS["exploit_available"]   * exploit_available
        + WEIGHTS["cvss"]                * cvss_norm
        + WEIGHTS["kev_ransomware"]      * kev_ransomware
        + WEIGHTS["business_criticality"]* biz_crit
        + WEIGHTS["threat_campaign_match"]* threat_match
        + WEIGHTS["days_open"]           * days_norm
    ) * 100

    # ── Penalty multipliers ────────────────────────────────────────────────
    penalty = 1.0
    if not bool(row.get("edr_installed", True)):
        penalty *= 1.15                         # No EDR = harder to detect
    if str(row.get("assigned_owner", "")).strip() == "":
        penalty *= 1.05                         # Unowned assets are slower to patch
    if str(row.get("stale_asset", "no")).lower() == "yes":
        penalty *= 1.05                         # Stale/unmanaged assets are higher risk

    raw = base * penalty
    return min(100.0, round(raw, 2))


def get_top_risks(master: pd.DataFrame, n: int = 5) -> list[dict[str, Any]]:
    """
    Score all vulnerability×asset rows and return the top-N risks as
    a list of rich dicts ready for the LLM and frontend.
    """
    if master.empty:
        return []

    master = master.copy()
    master["risk_score"] = master.apply(compute_score, axis=1)

    # De-duplicate: keep highest-scoring row per (asset_id, cve_id) pair
    master = (
        master
        .sort_values("risk_score", ascending=False)
        .drop_duplicates(subset=["asset_id", "cve_id"])
        .reset_index(drop=True)
    )

    top = master.head(n)

    results = []
    for rank, (_, row) in enumerate(top.iterrows(), start=1):
        result = {
            "rank": rank,
            "risk_score": float(row["risk_score"]),

            # Asset details
            "asset_id":       str(row.get("asset_id", "")),
            "asset_name":     str(row.get("asset_name", "")),
            "asset_type":     str(row.get("asset_type", "")),
            "environment":    str(row.get("environment", "")),
            "internet_exposed": bool(row.get("internet_exposed", False)),
            "edr_installed":  bool(row.get("edr_installed", True)),
            "asset_criticality": int(row.get("criticality", row.get("criticality_x", 3))),
            "owner_team":     str(row.get("owner_team", "")),
            "assigned_owner": str(row.get("assigned_owner", "Unassigned")),
            "vendor":         str(row.get("vendor", "")),
            "product":        str(row.get("product", "")),
            "version":        str(row.get("version", "")),
            "location":       str(row.get("location", "")),

            # Vulnerability details
            "vuln_id":           str(row.get("vuln_id", "")),
            "cve_id":            str(row.get("cve_id", "")),
            "cvss_score":        float(row.get("cvss_score", 0)),
            "severity":          str(row.get("severity", "")),
            "exploit_available": bool(row.get("exploit_available", False)),
            "patch_available":   bool(row.get("patch_available", True)),
            "days_open":         int(row.get("days_open", 0)),
            "vuln_description":  str(row.get("description", "")),
            "in_kev":            bool(row.get("in_kev", False)),
            "kev_ransomware":    bool(row.get("kev_ransomware", False)),

            # Threat intelligence
            "threat_campaign_match": bool(row.get("threat_campaign_match", False)),
            "campaign_names":   str(row.get("campaign_names", "")),
            "threat_actors":    str(row.get("threat_actors", "")),
            "ti_confidence":    str(row.get("max_confidence", "")),

            # Business context
            "business_service":    str(row.get("business_service", "")),
            "svc_customer_facing": str(row.get("svc_customer_facing", "")),
            "compliance_scope":    str(row.get("compliance_scope", "")),
            "revenue_impact_usd_per_hour": float(row.get("revenue_impact_usd_per_hour", 0)),
            "rto_hours":           float(row.get("rto_hours", 24)),
            "svc_criticality":     int(row.get("svc_criticality", 3)),

            # Score decomposition (for transparency)
            "score_breakdown": _breakdown(row),
        }
        results.append(result)

    logger.info(f"[scorer] Top-{n} risks scored. Highest: {results[0]['risk_score']:.1f}")
    return results


def _breakdown(row: pd.Series) -> dict[str, float]:
    """Return the individual component contributions (0–100 scale each)."""
    asset_crit = float(row.get("criticality", row.get("criticality_x", 3)))
    svc_crit   = float(row.get("svc_criticality", 3))
    return {
        "internet_exposed":      round(WEIGHTS["internet_exposed"]       * float(bool(row.get("internet_exposed", False))) * 100, 1),
        "exploit_available":     round(WEIGHTS["exploit_available"]      * float(bool(row.get("exploit_available", False))) * 100, 1),
        "cvss":                  round(WEIGHTS["cvss"]                   * _norm(float(row.get("cvss_score", 0)), 0, MAX_CVSS) * 100, 1),
        "kev_ransomware":        round(WEIGHTS["kev_ransomware"]         * float(bool(row.get("kev_ransomware", False))) * 100, 1),
        "business_criticality":  round(WEIGHTS["business_criticality"]   * _norm(max(asset_crit, svc_crit), 1, MAX_CRITICALITY) * 100, 1),
        "threat_campaign_match": round(WEIGHTS["threat_campaign_match"]  * float(bool(row.get("threat_campaign_match", False))) * 100, 1),
        "days_open":             round(WEIGHTS["days_open"]              * _norm(float(row.get("days_open", 0)), 0, MAX_DAYS_OPEN) * 100, 1),
    }

"""
llm_generator.py — TawasolPay Risk Assistant
Generates plain-English risk explanations and remediation summaries
using Google Gemini (gemini-3.6-flash, free tier).

Requires GEMINI_API_KEY environment variable to be set.
"""
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class LLMGenerator:
    """Generates structured plain-English risk output."""

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self._client  = None
        self._mode    = "gemini"

        if not self._api_key:
            logger.error("[LLM] CRITICAL: No GEMINI_API_KEY provided. This is a real AI project, fallbacks are disabled.")
            raise ValueError("GEMINI_API_KEY environment variable is required. No fallbacks allowed.")
            
        import google.generativeai as genai
        genai.configure(api_key=self._api_key)
        self._client = genai.GenerativeModel("gemini-3.6-flash")
        logger.info("[LLM] Using Google Gemini (gemini-3.6-flash)")

    @property
    def mode(self) -> str:
        return self._mode

    # ── Public API ─────────────────────────────────────────────────────────────

    def generate_risk_entry(self, risk: dict, nist_controls: list[dict], threat_report: str = "") -> dict:
        """
        Given a scored risk dict, retrieved NIST controls, and the MDR threat
        report, produce:
          - why_ranked_here:    plain-English ranking rationale (1–2 sentences)
          - executive_summary:  1-paragraph technical summary for a manager
          - remediation_action: concrete next-step sentence
          - nist_control:       the primary NIST control with explanation
        """
        primary_control = nist_controls[0] if nist_controls else {}

        return self._gemini_generate(risk, primary_control, threat_report)

    # ── Gemini Path ────────────────────────────────────────────────────────────

    def _gemini_generate(self, risk: dict, control: dict, threat_report: str = "") -> dict:
        prompt = self._build_prompt(risk, control, threat_report)
        ctrl_id = control.get("control_id", "N/A")
        logger.info(f"[LLM Step 1: Prompt Assembly] Prepared Gemini prompt for Rank #{risk['rank']} ({risk['cve_id']} on {risk['asset_name']}) + NIST {ctrl_id} + Threat Report ({len(threat_report)} chars)")
        try:
            logger.info(f"[LLM Step 2: Generation] Calling Google Gemini 3.6 Flash (gemini-3.6-flash)...")
            response = self._client.generate_content(prompt)
            text = response.text.strip()
            logger.info(f"[LLM Step 3: Parsing] Gemini response received ({len(text)} chars). Parsing 4 structured sections...")
            return self._parse_gemini_response(text, risk, control)
        except Exception as exc:
            logger.error(f"[LLM] Gemini call failed for Rank #{risk['rank']}: {exc}")
            raise

    def _build_prompt(self, risk: dict, control: dict, threat_report: str = "") -> str:
        campaign_info = ""
        if risk["threat_campaign_match"]:
            campaign_info = (
                f"Active threat campaigns: {risk['campaign_names']} "
                f"(actors: {risk['threat_actors']}, confidence: {risk['ti_confidence']}). "
                f"This CVE is being actively weaponised in the current wave of Gulf fintech attacks."
            )
        else:
            campaign_info = "No matching active threat campaign for this specific CVE."

        nist_text = control.get("control_text", "")[:800] if control else ""
        nist_id   = control.get("control_id", "N/A")
        nist_name = control.get("control_name", "N/A")

        # Include MDR threat report for situational awareness
        threat_section = ""
        if threat_report:
            threat_section = f"""\n\nMDR THREAT ADVISORY (received this morning — treat as current intelligence):
{threat_report[:2000]}
"""

        return f"""You are a senior cybersecurity analyst writing a risk report for TawasolPay's CISO Board briefing.

RISK DATA:
- Rank: #{risk['rank']} of 5
- Risk Score: {risk['risk_score']:.1f}/100
- Asset: {risk['asset_name']} ({risk['asset_type']}, {risk['environment']} environment)
- Vendor/Product: {risk['vendor']} {risk['product']} v{risk['version']}
- Internet Exposed: {risk['internet_exposed']}
- EDR Installed: {risk['edr_installed']}
- Vulnerability: {risk['cve_id']} (CVSS {risk['cvss_score']})
- Description: {risk['vuln_description']}
- Exploit Available: {risk['exploit_available']}
- Patch Available: {risk['patch_available']}
- Days Open: {risk['days_open']}
- In CISA KEV: {risk['in_kev']}
- KEV Ransomware Use: {risk['kev_ransomware']}
- Business Service: {risk['business_service']} (criticality: {risk['svc_criticality']}/5)
- Revenue Impact if Down: ${risk['revenue_impact_usd_per_hour']:,.0f}/hour
- Compliance Scope: {risk['compliance_scope']}
- {campaign_info}
{threat_section}
RETRIEVED NIST CONTROL ({nist_id} — {nist_name}):
{nist_text}

Write a structured risk entry with EXACTLY these four sections. Be direct and specific — no fluff.

WHY_RANKED_HERE: (1–2 sentences explaining this specific rank — mention the key factors that elevated it)

EXECUTIVE_SUMMARY: (2–3 sentences: asset, CVE, exposure context, business risk, threat landscape context)

REMEDIATION_ACTION: (1 sentence: the single most important immediate action)

NIST_CONTROL_GUIDANCE: (2–3 sentences: what NIST {nist_id} recommends for this specific situation — quote from the control text)
"""

    def _parse_gemini_response(self, text: str, risk: dict, control: dict) -> dict:
        sections = {
            "why_ranked_here":      "",
            "executive_summary":    "",
            "remediation_action":   "",
            "nist_control_guidance": "",
        }
        markers = {
            "WHY_RANKED_HERE":       "why_ranked_here",
            "EXECUTIVE_SUMMARY":     "executive_summary",
            "REMEDIATION_ACTION":    "remediation_action",
            "NIST_CONTROL_GUIDANCE": "nist_control_guidance",
        }
        current = None
        buf = []
        for line in text.splitlines():
            matched = False
            for marker, key in markers.items():
                if line.strip().upper().startswith(marker):
                    if current:
                        sections[current] = " ".join(buf).strip()
                    current = key
                    buf = [line.split(":", 1)[-1].strip()] if ":" in line else []
                    matched = True
                    break
            if not matched and current:
                buf.append(line.strip())
        if current:
            sections[current] = " ".join(buf).strip()

        # Remove template filling logic
        for key in sections:
            if not sections[key]:
                sections[key] = "[Gemini did not generate this section — review prompt.]"

        sections["nist_control"] = {
            "control_id":   control.get("control_id", ""),
            "control_name": control.get("control_name", ""),
            "family":       control.get("family", ""),
            "control_text": control.get("control_text", ""),
            "source":       control.get("source", "NIST SP 800-53 Rev. 5"),
        }
        sections["generated_by"] = "gemini-3.6-flash"
        return sections


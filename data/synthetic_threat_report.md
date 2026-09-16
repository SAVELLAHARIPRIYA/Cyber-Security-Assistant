# TawasolPay MDR Advisory — Synthetic Threat Report

**CLASSIFICATION: TLP:AMBER — RESTRICTED DISTRIBUTION**
**FROM:** Gulf Shield MDR Operations Centre
**TO:** TawasolPay CISO Office
**DATE:** 15 April 2024, 07:30 GST
**SUBJECT:** URGENT — Active Ransomware Campaigns Targeting Gulf FinTech Infrastructure

---

## Executive Summary

Gulf Shield MDR has identified three active, coordinated threat campaigns currently targeting fintech and digital payment operators across the Gulf Cooperation Council (GCC) region. At least two operators in the UAE payment sector have confirmed incidents in the past 72 hours. TawasolPay's infrastructure profile overlaps significantly with the attack surface observed in confirmed compromises.

**Immediate action is required.** This advisory supersedes all prior threat intelligence on these actor groups.

---

## Campaign 1: GULFSTRIKE (UNC4841)

**Status:** Active — confirmed UAE fintech incidents in last 72 hours
**Threat Actor:** UNC4841 (Mandiant attribution, high confidence)
**Primary Objective:** Ransomware deployment (ALPHV/BlackCat affiliate), data exfiltration prior to encryption
**Ransom demands observed:** USD 2.5M – USD 8M

**Key CVEs being actively weaponised:**
- **CVE-2023-4966 (Citrix Bleed)** — Session token hijacking on NetScaler ADC/Gateway devices. TawasolPay is confirmed to run Citrix NetScaler. IOC match rate: HIGH.
- **CVE-2021-44228 (Log4Shell)** — Persistent exploitation of unpatched Log4j deployments. Actor has automated scanning for exposed JNDI endpoints.
- **CVE-2022-26134 (Confluence RCE)** — Used as initial access vector into dev environments with lateral movement to production.
- **CVE-2022-47966 (ManageEngine)** — SAML token forgery for initial authentication bypass.
- **CVE-2022-30190 (Follina)** — Phishing lure delivery via malicious Office documents targeting finance and compliance teams.
- **CVE-2020-1472 (Zerologon)** — Post-exploitation domain takeover once initial access established.

**TTPs:** Initial access via internet-exposed appliances → credential harvesting → Active Directory compromise via Zerologon/certifried → ransomware detonation across network shares. Average dwell time before detonation: 4–8 days.

**IOC Count:** 47 network indicators, 12 host-based indicators published to threat intel platform.

---

## Campaign 2: BLACKMINT (Scattered Spider / UNC3944)

**Status:** Active — escalating activity in last 14 days
**Threat Actor:** Scattered Spider (also tracked as UNC3944 / Roasted 0ktapus)
**Primary Objective:** Identity system compromise → social engineering → ransomware (ALPHV affiliate)
**Notable:** This group successfully compromised MGM Resorts and Caesars Palace via identity platform attacks.

**Key CVEs being actively weaponised:**
- **CVE-2024-21762 (Fortinet SSL VPN)** — Critical OOB write, unauthenticated RCE. Active exploitation confirmed against UAE-based targets. Patch not available for all affected versions as of advisory date.
- **CVE-2022-1388 (F5 BIG-IP)** — iControl REST API unauthenticated RCE. Load balancers and ADCs are primary targets.
- **CVE-2023-42793 (JetBrains TeamCity)** — CI/CD pipeline compromise for supply chain access. Dev-to-prod lateral movement observed.
- **CVE-2023-23397 (Microsoft Outlook)** — NTLM credential theft via calendar invites, used to harvest VPN credentials from finance and payments teams.
- **CVE-2023-48788 (Fortinet EMS)** — SQL injection for unauthenticated access to endpoint management.
- **CVE-2023-27350 (PaperCut)** — Authentication bypass used in printer/document workflow servers which often have high network trust.

**TTPs:** SIM-swapping + MFA fatigue attacks → identity provider compromise → lateral movement via stolen credentials → ransomware. Group is known for calling help desks to social engineer password resets.

**IOC Count:** 33 network indicators, 9 host-based indicators.

---

## Campaign 3: DARKNEXUS (Lazarus Group / APT38)

**Status:** Active — financial sector targeting confirmed
**Threat Actor:** Lazarus Group (DPRK state-sponsored), APT38 financial theft sub-cluster
**Primary Objective:** SWIFT/payment rail infiltration, cryptocurrency theft, ransomware as secondary objective
**Funds stolen to date (2024):** Estimated USD 300M across multiple incidents

**Key CVEs being actively weaponised:**
- **CVE-2024-3400 (PAN-OS)** — Zero-day (now patched) OS command injection via GlobalProtect. Lazarus has operational playbooks for this CVE and is actively scanning for unpatched devices.
- **CVE-2023-28252 (Windows CLFS)** — Privilege escalation used post-initial access to achieve SYSTEM.
- **CVE-2021-26855 (ProxyLogon)** — Still used as initial access against unpatched Exchange servers for establishing persistent mail access.
- **CVE-2022-41082 (ProxyNotShell)** — Chained with ProxyLogon for reliable Exchange RCE.
- **CVE-2021-27065 (Exchange file write)** — Used to drop webshells in Exchange OWA directories for persistent access.
- **CVE-2023-32315 (Openfire)** — Targeting XMPP/messaging infrastructure for C2 communication channels.
- **CVE-2023-35078 (Ivanti EPMM)** — Mobile device management platform compromise for endpoint visibility.
- **CVE-2024-1709 (ConnectWise)** — Remote access tool exploitation for persistent operator access.

**TTPs:** Spearphishing → VPN/perimeter device exploitation → Living off the Land (LOLBins) → payment rail reconnaissance → fund transfer manipulation. Group maintains access for weeks to months before action.

**IOC Count:** 28 network indicators, 15 host-based indicators.

---

## Immediate Recommended Actions

1. **Priority 1 — Citrix NetScaler (CVE-2023-4966):** Apply hotfix immediately. Terminate ALL active sessions. Rotate session tokens. Assume session tokens are compromised if patch has not been applied.

2. **Priority 2 — Fortinet SSL VPN (CVE-2024-21762):** Apply patch or disable SSL VPN. This vulnerability has no workaround. Assume RCE if exposed and unpatched.

3. **Priority 3 — PAN-OS (CVE-2024-3400):** Apply patch. Check GlobalProtect logs for `/css?user=` patterns indicating exploitation attempts.

4. **Priority 4 — Log4Shell (CVE-2021-44228):** Any system still running Log4j 2.14.1 or earlier must be treated as potentially compromised. Uplift to 2.17.1+ immediately.

5. **Priority 5 — Active Directory:** Run BloodHound assessment. Ensure Zerologon (CVE-2020-1472) patch is applied to ALL domain controllers.

**MDR Hotline:** +971-4-XXX-XXXX (24/7 Incident Response)
**Threat Intel Portal:** https://ti.gulfshield-mdr.ae (credentials in secure channel)

---

*This report was compiled using telemetry from Gulf Shield MDR sensors, ISAC sharing, and commercial threat intelligence feeds. CVE data cross-referenced with CISA KEV catalog as of 14 April 2024.*

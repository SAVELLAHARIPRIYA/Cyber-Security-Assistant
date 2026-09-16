"""
TawasolPay Synthetic Data Generator
Generates all CSV files for the AI Cyber Risk Assistant.
Run: python generate_data.py
"""
import csv
import os
from datetime import datetime, timedelta
import random

random.seed(42)
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def w(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Wrote {len(rows)} rows -> {os.path.basename(path)}")

# ─── 1. BUSINESS SERVICES (20) ─────────────────────────────────────────────
services = [
    {"service_id": "SVC-01", "service_name": "Digital Payment Processing",     "owner_team": "Payments",      "customer_facing": "yes", "compliance_scope": "PCI DSS,SOC2",           "revenue_impact_usd_per_hour": 450000, "rto_hours": 1,  "criticality": 5, "service_dependencies": "SVC-03,SVC-05"},
    {"service_id": "SVC-02", "service_name": "Identity Verification Service",  "owner_team": "Identity",      "customer_facing": "yes", "compliance_scope": "GDPR,PCI DSS,ISO 27001", "revenue_impact_usd_per_hour": 200000, "rto_hours": 2,  "criticality": 5, "service_dependencies": "SVC-04"},
    {"service_id": "SVC-03", "service_name": "Card Tokenization Service",      "owner_team": "Payments",      "customer_facing": "yes", "compliance_scope": "PCI DSS",                "revenue_impact_usd_per_hour": 300000, "rto_hours": 1,  "criticality": 5, "service_dependencies": "SVC-01"},
    {"service_id": "SVC-04", "service_name": "KYC / AML Processing",           "owner_team": "Compliance",    "customer_facing": "yes", "compliance_scope": "GDPR,ISO 27001",         "revenue_impact_usd_per_hour": 150000, "rto_hours": 4,  "criticality": 5, "service_dependencies": "SVC-02"},
    {"service_id": "SVC-05", "service_name": "Fraud Detection Engine",         "owner_team": "Risk",          "customer_facing": "no",  "compliance_scope": "PCI DSS,SOC2",           "revenue_impact_usd_per_hour": 500000, "rto_hours": 2,  "criticality": 5, "service_dependencies": "SVC-01,SVC-03"},
    {"service_id": "SVC-06", "service_name": "Merchant Payment API",           "owner_team": "Payments",      "customer_facing": "yes", "compliance_scope": "PCI DSS,SOC2",           "revenue_impact_usd_per_hour": 200000, "rto_hours": 2,  "criticality": 4, "service_dependencies": "SVC-01"},
    {"service_id": "SVC-07", "service_name": "Customer Mobile App Backend",    "owner_team": "Mobile",        "customer_facing": "yes", "compliance_scope": "GDPR,SOC2",              "revenue_impact_usd_per_hour": 100000, "rto_hours": 4,  "criticality": 4, "service_dependencies": "SVC-02,SVC-01"},
    {"service_id": "SVC-08", "service_name": "Transaction Monitoring",         "owner_team": "Risk",          "customer_facing": "no",  "compliance_scope": "SOC2,ISO 27001",         "revenue_impact_usd_per_hour": 0,      "rto_hours": 8,  "criticality": 4, "service_dependencies": "SVC-01,SVC-05"},
    {"service_id": "SVC-09", "service_name": "Customer Portal",                "owner_team": "Web",           "customer_facing": "yes", "compliance_scope": "GDPR",                   "revenue_impact_usd_per_hour": 50000,  "rto_hours": 8,  "criticality": 3, "service_dependencies": "SVC-02,SVC-07"},
    {"service_id": "SVC-10", "service_name": "Settlement Processing",          "owner_team": "Payments",      "customer_facing": "no",  "compliance_scope": "PCI DSS,SOC2",           "revenue_impact_usd_per_hour": 300000, "rto_hours": 2,  "criticality": 5, "service_dependencies": "SVC-01,SVC-03"},
    {"service_id": "SVC-11", "service_name": "Reconciliation Service",         "owner_team": "Finance",       "customer_facing": "no",  "compliance_scope": "SOC2",                   "revenue_impact_usd_per_hour": 100000, "rto_hours": 4,  "criticality": 4, "service_dependencies": "SVC-10"},
    {"service_id": "SVC-12", "service_name": "Partner Integration API",        "owner_team": "Partnerships",  "customer_facing": "yes", "compliance_scope": "SOC2",                   "revenue_impact_usd_per_hour": 50000,  "rto_hours": 8,  "criticality": 3, "service_dependencies": "SVC-06"},
    {"service_id": "SVC-13", "service_name": "Compliance Reporting Platform",  "owner_team": "Compliance",    "customer_facing": "no",  "compliance_scope": "ISO 27001,GDPR",         "revenue_impact_usd_per_hour": 0,      "rto_hours": 24, "criticality": 3, "service_dependencies": "SVC-04,SVC-08"},
    {"service_id": "SVC-14", "service_name": "Admin Dashboard",                "owner_team": "IT Ops",        "customer_facing": "no",  "compliance_scope": "ISO 27001",              "revenue_impact_usd_per_hour": 0,      "rto_hours": 24, "criticality": 3, "service_dependencies": "SVC-13"},
    {"service_id": "SVC-15", "service_name": "SMS / OTP Notification Service", "owner_team": "Identity",      "customer_facing": "yes", "compliance_scope": "GDPR",                   "revenue_impact_usd_per_hour": 30000,  "rto_hours": 4,  "criticality": 4, "service_dependencies": "SVC-02"},
    {"service_id": "SVC-16", "service_name": "Email Notification Service",     "owner_team": "Platform",      "customer_facing": "yes", "compliance_scope": "GDPR",                   "revenue_impact_usd_per_hour": 10000,  "rto_hours": 8,  "criticality": 3, "service_dependencies": "SVC-09"},
    {"service_id": "SVC-17", "service_name": "Analytics & BI Platform",        "owner_team": "Data",          "customer_facing": "no",  "compliance_scope": "SOC2",                   "revenue_impact_usd_per_hour": 0,      "rto_hours": 48, "criticality": 2, "service_dependencies": "SVC-08"},
    {"service_id": "SVC-18", "service_name": "DevOps CI/CD Pipeline",          "owner_team": "DevOps",        "customer_facing": "no",  "compliance_scope": "ISO 27001",              "revenue_impact_usd_per_hour": 0,      "rto_hours": 24, "criticality": 2, "service_dependencies": ""},
    {"service_id": "SVC-19", "service_name": "Internal IT Services",           "owner_team": "IT Ops",        "customer_facing": "no",  "compliance_scope": "ISO 27001",              "revenue_impact_usd_per_hour": 0,      "rto_hours": 48, "criticality": 2, "service_dependencies": ""},
    {"service_id": "SVC-20", "service_name": "Logging & SIEM",                 "owner_team": "Security",      "customer_facing": "no",  "compliance_scope": "ISO 27001,SOC2",         "revenue_impact_usd_per_hour": 0,      "rto_hours": 8,  "criticality": 3, "service_dependencies": ""},
]

# ─── 2. ASSETS (60) ────────────────────────────────────────────────────────
# Designed to include high-risk internet-exposed prod assets, internal
# critical servers, dev servers, and some stale/unowned assets.
assets = [
    # === PRODUCTION UAE — Internet-Exposed (High Criticality) ===
    {"asset_id":"ASSET-001","asset_name":"PayGateway-UAE-Prod-01","asset_type":"Application Server","environment":"production","owner_team":"Payments","business_service":"Digital Payment Processing","internet_exposed":"yes","criticality":5,"edr_installed":"no","vendor":"Citrix","product":"NetScaler ADC","version":"13.1-37.38","ip_address":"185.220.10.1","location":"UAE-DC1","last_updated":"2024-01-15","stale_asset":"no","assigned_owner":"Ali Hassan"},
    {"asset_id":"ASSET-002","asset_name":"PayGateway-UAE-Prod-02","asset_type":"Application Server","environment":"production","owner_team":"Payments","business_service":"Digital Payment Processing","internet_exposed":"yes","criticality":5,"edr_installed":"yes","vendor":"Citrix","product":"NetScaler ADC","version":"13.1-37.38","ip_address":"185.220.10.2","location":"UAE-DC1","last_updated":"2024-01-15","stale_asset":"no","assigned_owner":"Ali Hassan"},
    {"asset_id":"ASSET-003","asset_name":"IdentityAPI-UAE-Prod-01","asset_type":"API Server","environment":"production","owner_team":"Identity","business_service":"Identity Verification Service","internet_exposed":"yes","criticality":5,"edr_installed":"no","vendor":"Fortinet","product":"FortiOS SSL VPN","version":"7.4.0","ip_address":"185.220.10.3","location":"UAE-DC1","last_updated":"2023-12-01","stale_asset":"no","assigned_owner":"Priya Sharma"},
    {"asset_id":"ASSET-004","asset_name":"IdentityAPI-UAE-Prod-02","asset_type":"API Server","environment":"production","owner_team":"Identity","business_service":"Identity Verification Service","internet_exposed":"yes","criticality":5,"edr_installed":"yes","vendor":"Fortinet","product":"FortiOS SSL VPN","version":"7.4.0","ip_address":"185.220.10.4","location":"UAE-DC1","last_updated":"2023-12-01","stale_asset":"no","assigned_owner":"Priya Sharma"},
    {"asset_id":"ASSET-005","asset_name":"CardProc-UAE-Prod-01","asset_type":"Application Server","environment":"production","owner_team":"Payments","business_service":"Card Tokenization Service","internet_exposed":"yes","criticality":5,"edr_installed":"yes","vendor":"F5 Networks","product":"BIG-IP","version":"14.1.4","ip_address":"185.220.10.5","location":"UAE-DC1","last_updated":"2024-02-20","stale_asset":"no","assigned_owner":"Omar Al-Rashid"},
    {"asset_id":"ASSET-006","asset_name":"CardProc-UAE-Prod-02","asset_type":"Application Server","environment":"production","owner_team":"Payments","business_service":"Card Tokenization Service","internet_exposed":"yes","criticality":5,"edr_installed":"yes","vendor":"F5 Networks","product":"BIG-IP","version":"14.1.4","ip_address":"185.220.10.6","location":"UAE-DC1","last_updated":"2024-02-20","stale_asset":"no","assigned_owner":"Omar Al-Rashid"},
    {"asset_id":"ASSET-007","asset_name":"APIGateway-UAE-Prod-01","asset_type":"Network Appliance","environment":"production","owner_team":"Platform","business_service":"Merchant Payment API","internet_exposed":"yes","criticality":4,"edr_installed":"yes","vendor":"Palo Alto Networks","product":"PAN-OS","version":"11.1.0","ip_address":"185.220.10.7","location":"UAE-DC1","last_updated":"2024-03-01","stale_asset":"no","assigned_owner":"Ravi Kumar"},
    {"asset_id":"ASSET-008","asset_name":"APIGateway-UAE-Prod-02","asset_type":"Network Appliance","environment":"production","owner_team":"Platform","business_service":"Merchant Payment API","internet_exposed":"yes","criticality":4,"edr_installed":"yes","vendor":"Palo Alto Networks","product":"PAN-OS","version":"11.1.0","ip_address":"185.220.10.8","location":"UAE-DC1","last_updated":"2024-03-01","stale_asset":"no","assigned_owner":"Ravi Kumar"},
    {"asset_id":"ASSET-009","asset_name":"WebLB-UAE-Prod-01","asset_type":"Load Balancer","environment":"production","owner_team":"IT Ops","business_service":"Customer Portal","internet_exposed":"yes","criticality":4,"edr_installed":"yes","vendor":"HAProxy","product":"HAProxy","version":"2.6.1","ip_address":"185.220.10.9","location":"UAE-DC1","last_updated":"2024-04-01","stale_asset":"no","assigned_owner":"Farid Al-Mansouri"},
    {"asset_id":"ASSET-010","asset_name":"WebLB-UAE-Prod-02","asset_type":"Load Balancer","environment":"production","owner_team":"IT Ops","business_service":"Customer Portal","internet_exposed":"yes","criticality":4,"edr_installed":"yes","vendor":"HAProxy","product":"HAProxy","version":"2.6.1","ip_address":"185.220.10.10","location":"UAE-DC1","last_updated":"2024-04-01","stale_asset":"no","assigned_owner":"Farid Al-Mansouri"},
    {"asset_id":"ASSET-011","asset_name":"VPNGateway-UAE-Prod-01","asset_type":"VPN Gateway","environment":"production","owner_team":"IT Ops","business_service":"Internal IT Services","internet_exposed":"yes","criticality":4,"edr_installed":"no","vendor":"Cisco","product":"IOS XE","version":"17.3.4a","ip_address":"185.220.10.11","location":"UAE-DC1","last_updated":"2023-11-01","stale_asset":"no","assigned_owner":"Farid Al-Mansouri"},
    {"asset_id":"ASSET-012","asset_name":"VPNGateway-UAE-Prod-02","asset_type":"VPN Gateway","environment":"production","owner_team":"IT Ops","business_service":"Internal IT Services","internet_exposed":"yes","criticality":4,"edr_installed":"yes","vendor":"Cisco","product":"IOS XE","version":"17.3.4a","ip_address":"185.220.10.12","location":"UAE-DC1","last_updated":"2023-11-01","stale_asset":"no","assigned_owner":"Farid Al-Mansouri"},
    {"asset_id":"ASSET-013","asset_name":"EmailGateway-UAE-Prod-01","asset_type":"Mail Server","environment":"production","owner_team":"Platform","business_service":"Email Notification Service","internet_exposed":"yes","criticality":3,"edr_installed":"yes","vendor":"Microsoft","product":"Exchange Server","version":"2019 CU12","ip_address":"185.220.10.13","location":"UAE-DC1","last_updated":"2024-01-10","stale_asset":"no","assigned_owner":"Sara Al-Hamdan"},
    {"asset_id":"ASSET-014","asset_name":"WebPortal-UAE-Prod-01","asset_type":"Web Server","environment":"production","owner_team":"Web","business_service":"Customer Portal","internet_exposed":"yes","criticality":3,"edr_installed":"yes","vendor":"Apache","product":"HTTP Server","version":"2.4.51","ip_address":"185.220.10.14","location":"UAE-DC1","last_updated":"2024-02-01","stale_asset":"no","assigned_owner":"Sara Al-Hamdan"},
    {"asset_id":"ASSET-015","asset_name":"WebPortal-UAE-Prod-02","asset_type":"Web Server","environment":"production","owner_team":"Web","business_service":"Customer Portal","internet_exposed":"yes","criticality":3,"edr_installed":"yes","vendor":"Apache","product":"HTTP Server","version":"2.4.51","ip_address":"185.220.10.15","location":"UAE-DC1","last_updated":"2024-02-01","stale_asset":"no","assigned_owner":"Sara Al-Hamdan"},

    # === PRODUCTION UAE — Internal (High Criticality) ===
    {"asset_id":"ASSET-016","asset_name":"FraudEngine-UAE-Prod-01","asset_type":"Application Server","environment":"production","owner_team":"Risk","business_service":"Fraud Detection Engine","internet_exposed":"no","criticality":5,"edr_installed":"no","vendor":"Apache","product":"Log4j / Spring Boot","version":"2.14.1","ip_address":"10.10.1.16","location":"UAE-DC1","last_updated":"2022-08-01","stale_asset":"no","assigned_owner":""},
    {"asset_id":"ASSET-017","asset_name":"FraudEngine-UAE-Prod-02","asset_type":"Application Server","environment":"production","owner_team":"Risk","business_service":"Fraud Detection Engine","internet_exposed":"no","criticality":5,"edr_installed":"no","vendor":"Apache","product":"Log4j / Spring Boot","version":"2.14.1","ip_address":"10.10.1.17","location":"UAE-DC1","last_updated":"2022-08-01","stale_asset":"no","assigned_owner":""},
    {"asset_id":"ASSET-018","asset_name":"CoreDB-UAE-Prod-01","asset_type":"Database Server","environment":"production","owner_team":"Data","business_service":"Digital Payment Processing","internet_exposed":"no","criticality":5,"edr_installed":"yes","vendor":"Microsoft","product":"SQL Server","version":"2019","ip_address":"10.10.1.18","location":"UAE-DC1","last_updated":"2024-03-15","stale_asset":"no","assigned_owner":"Arun Nair"},
    {"asset_id":"ASSET-019","asset_name":"CoreDB-UAE-Prod-02","asset_type":"Database Server","environment":"production","owner_team":"Data","business_service":"Digital Payment Processing","internet_exposed":"no","criticality":5,"edr_installed":"yes","vendor":"Microsoft","product":"SQL Server","version":"2019","ip_address":"10.10.1.19","location":"UAE-DC1","last_updated":"2024-03-15","stale_asset":"no","assigned_owner":"Arun Nair"},
    {"asset_id":"ASSET-020","asset_name":"KYCServer-UAE-Prod-01","asset_type":"Application Server","environment":"production","owner_team":"Compliance","business_service":"KYC / AML Processing","internet_exposed":"no","criticality":5,"edr_installed":"yes","vendor":"JetBrains","product":"TeamCity","version":"2023.05.3","ip_address":"10.10.1.20","location":"UAE-DC1","last_updated":"2023-10-01","stale_asset":"no","assigned_owner":"Layla Al-Zaabi"},
    {"asset_id":"ASSET-021","asset_name":"SettlementSrv-UAE-Prod-01","asset_type":"Application Server","environment":"production","owner_team":"Finance","business_service":"Settlement Processing","internet_exposed":"no","criticality":5,"edr_installed":"yes","vendor":"Oracle","product":"WebLogic","version":"12.2.1.4","ip_address":"10.10.1.21","location":"UAE-DC1","last_updated":"2023-09-01","stale_asset":"no","assigned_owner":"Nasser Al-Kaabi"},
    {"asset_id":"ASSET-022","asset_name":"SettlementSrv-UAE-Prod-02","asset_type":"Application Server","environment":"production","owner_team":"Finance","business_service":"Settlement Processing","internet_exposed":"no","criticality":5,"edr_installed":"yes","vendor":"Oracle","product":"WebLogic","version":"12.2.1.4","ip_address":"10.10.1.22","location":"UAE-DC1","last_updated":"2023-09-01","stale_asset":"no","assigned_owner":"Nasser Al-Kaabi"},
    {"asset_id":"ASSET-023","asset_name":"DomainController-UAE-01","asset_type":"Directory Service","environment":"production","owner_team":"IT Ops","business_service":"Internal IT Services","internet_exposed":"no","criticality":5,"edr_installed":"yes","vendor":"Microsoft","product":"Active Directory","version":"Windows Server 2019","ip_address":"10.10.1.23","location":"UAE-DC1","last_updated":"2024-01-20","stale_asset":"no","assigned_owner":"Farid Al-Mansouri"},
    {"asset_id":"ASSET-024","asset_name":"DomainController-UAE-02","asset_type":"Directory Service","environment":"production","owner_team":"IT Ops","business_service":"Internal IT Services","internet_exposed":"no","criticality":5,"edr_installed":"yes","vendor":"Microsoft","product":"Active Directory","version":"Windows Server 2019","ip_address":"10.10.1.24","location":"UAE-DC1","last_updated":"2024-01-20","stale_asset":"no","assigned_owner":"Farid Al-Mansouri"},
    {"asset_id":"ASSET-025","asset_name":"TxnMonitor-UAE-Prod-01","asset_type":"Application Server","environment":"production","owner_team":"Risk","business_service":"Transaction Monitoring","internet_exposed":"no","criticality":4,"edr_installed":"yes","vendor":"Elastic","product":"Elasticsearch","version":"7.17.5","ip_address":"10.10.1.25","location":"UAE-DC1","last_updated":"2024-02-10","stale_asset":"no","assigned_owner":"Mona Al-Ali"},
    {"asset_id":"ASSET-026","asset_name":"SIEM-UAE-Prod-01","asset_type":"Security Appliance","environment":"production","owner_team":"Security","business_service":"Logging & SIEM","internet_exposed":"no","criticality":4,"edr_installed":"yes","vendor":"Splunk","product":"Splunk Enterprise","version":"9.0.3","ip_address":"10.10.1.26","location":"UAE-DC1","last_updated":"2024-03-01","stale_asset":"no","assigned_owner":"Khalid Al-Sayed"},
    {"asset_id":"ASSET-027","asset_name":"AppServer-UAE-Prod-01","asset_type":"Application Server","environment":"production","owner_team":"Mobile","business_service":"Customer Mobile App Backend","internet_exposed":"no","criticality":4,"edr_installed":"yes","vendor":"Node.js","product":"Express","version":"18.12.0","ip_address":"10.10.1.27","location":"UAE-DC1","last_updated":"2024-04-05","stale_asset":"no","assigned_owner":"Zaid Al-Farsi"},
    {"asset_id":"ASSET-028","asset_name":"AppServer-UAE-Prod-02","asset_type":"Application Server","environment":"production","owner_team":"Mobile","business_service":"Customer Mobile App Backend","internet_exposed":"no","criticality":4,"edr_installed":"yes","vendor":"Node.js","product":"Express","version":"18.12.0","ip_address":"10.10.1.28","location":"UAE-DC1","last_updated":"2024-04-05","stale_asset":"no","assigned_owner":"Zaid Al-Farsi"},
    {"asset_id":"ASSET-029","asset_name":"ComplianceSrv-UAE-01","asset_type":"Application Server","environment":"production","owner_team":"Compliance","business_service":"Compliance Reporting Platform","internet_exposed":"no","criticality":3,"edr_installed":"yes","vendor":"ManageEngine","product":"ServiceDesk Plus","version":"14.2","ip_address":"10.10.1.29","location":"UAE-DC1","last_updated":"2023-06-01","stale_asset":"yes","assigned_owner":""},
    {"asset_id":"ASSET-030","asset_name":"LogServer-UAE-Prod-01","asset_type":"Log Server","environment":"production","owner_team":"Security","business_service":"Logging & SIEM","internet_exposed":"no","criticality":3,"edr_installed":"yes","vendor":"Graylog","product":"Graylog","version":"5.1.2","ip_address":"10.10.1.30","location":"UAE-DC1","last_updated":"2024-01-05","stale_asset":"no","assigned_owner":"Khalid Al-Sayed"},

    # === DEVELOPMENT INDIA — Internal (Low Criticality) ===
    {"asset_id":"ASSET-031","asset_name":"DevApp-IND-01","asset_type":"Application Server","environment":"development","owner_team":"DevOps","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":2,"edr_installed":"no","vendor":"JetBrains","product":"TeamCity","version":"2023.05.3","ip_address":"10.20.1.31","location":"IND-DC1","last_updated":"2023-11-01","stale_asset":"no","assigned_owner":"Vikram Singh"},
    {"asset_id":"ASSET-032","asset_name":"DevApp-IND-02","asset_type":"Application Server","environment":"development","owner_team":"DevOps","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":2,"edr_installed":"no","vendor":"Jenkins","product":"Jenkins","version":"2.387.3","ip_address":"10.20.1.32","location":"IND-DC1","last_updated":"2023-10-01","stale_asset":"no","assigned_owner":"Vikram Singh"},
    {"asset_id":"ASSET-033","asset_name":"DevDB-IND-01","asset_type":"Database Server","environment":"development","owner_team":"Data","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":2,"edr_installed":"no","vendor":"MySQL","product":"MySQL","version":"8.0.32","ip_address":"10.20.1.33","location":"IND-DC1","last_updated":"2024-01-01","stale_asset":"no","assigned_owner":"Deepa Nair"},
    {"asset_id":"ASSET-034","asset_name":"DevDB-IND-02","asset_type":"Database Server","environment":"development","owner_team":"Data","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":2,"edr_installed":"no","vendor":"PostgreSQL","product":"PostgreSQL","version":"15.2","ip_address":"10.20.1.34","location":"IND-DC1","last_updated":"2024-01-01","stale_asset":"no","assigned_owner":"Deepa Nair"},
    {"asset_id":"ASSET-035","asset_name":"CICD-IND-01","asset_type":"Build Server","environment":"development","owner_team":"DevOps","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":2,"edr_installed":"no","vendor":"GitLab","product":"GitLab CE","version":"16.1.0","ip_address":"10.20.1.35","location":"IND-DC1","last_updated":"2023-12-15","stale_asset":"no","assigned_owner":"Rahul Dev"},
    {"asset_id":"ASSET-036","asset_name":"TestSrv-IND-01","asset_type":"Test Server","environment":"development","owner_team":"QA","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":1,"edr_installed":"no","vendor":"Apache","product":"Tomcat","version":"9.0.65","ip_address":"10.20.1.36","location":"IND-DC1","last_updated":"2023-08-01","stale_asset":"yes","assigned_owner":""},
    {"asset_id":"ASSET-037","asset_name":"TestSrv-IND-02","asset_type":"Test Server","environment":"development","owner_team":"QA","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":1,"edr_installed":"no","vendor":"Apache","product":"Tomcat","version":"9.0.65","ip_address":"10.20.1.37","location":"IND-DC1","last_updated":"2023-08-01","stale_asset":"yes","assigned_owner":""},
    {"asset_id":"ASSET-038","asset_name":"DevAPI-IND-01","asset_type":"API Server","environment":"development","owner_team":"DevOps","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":2,"edr_installed":"no","vendor":"Python","product":"FastAPI","version":"0.95.1","ip_address":"10.20.1.38","location":"IND-DC1","last_updated":"2024-02-01","stale_asset":"no","assigned_owner":"Ankit Patel"},
    {"asset_id":"ASSET-039","asset_name":"DevApp-IND-03","asset_type":"Application Server","environment":"development","owner_team":"Payments","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":2,"edr_installed":"no","vendor":"Apache","product":"Log4j / Spring Boot","version":"2.14.1","ip_address":"10.20.1.39","location":"IND-DC1","last_updated":"2022-12-01","stale_asset":"yes","assigned_owner":""},
    {"asset_id":"ASSET-040","asset_name":"DevTools-IND-01","asset_type":"Application Server","environment":"development","owner_team":"DevOps","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":2,"edr_installed":"no","vendor":"Atlassian","product":"Confluence","version":"7.19.0","ip_address":"10.20.1.40","location":"IND-DC1","last_updated":"2023-07-01","stale_asset":"no","assigned_owner":"Rahul Dev"},
    {"asset_id":"ASSET-041","asset_name":"DevTools-IND-02","asset_type":"Application Server","environment":"development","owner_team":"DevOps","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":2,"edr_installed":"no","vendor":"Atlassian","product":"Jira","version":"9.4.0","ip_address":"10.20.1.41","location":"IND-DC1","last_updated":"2023-07-01","stale_asset":"no","assigned_owner":"Rahul Dev"},
    {"asset_id":"ASSET-042","asset_name":"DevMonitor-IND-01","asset_type":"Monitor Server","environment":"development","owner_team":"DevOps","business_service":"Logging & SIEM","internet_exposed":"no","criticality":1,"edr_installed":"no","vendor":"Grafana","product":"Grafana","version":"9.5.2","ip_address":"10.20.1.42","location":"IND-DC1","last_updated":"2023-09-01","stale_asset":"no","assigned_owner":"Ankit Patel"},
    {"asset_id":"ASSET-043","asset_name":"DevSec-IND-01","asset_type":"Security Scanner","environment":"development","owner_team":"Security","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":1,"edr_installed":"no","vendor":"Nessus","product":"Tenable Nessus","version":"10.5.0","ip_address":"10.20.1.43","location":"IND-DC1","last_updated":"2024-01-01","stale_asset":"no","assigned_owner":"Priya Dev"},
    {"asset_id":"ASSET-044","asset_name":"DockerHost-IND-01","asset_type":"Container Host","environment":"development","owner_team":"DevOps","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":2,"edr_installed":"no","vendor":"Docker","product":"Docker Engine","version":"23.0.3","ip_address":"10.20.1.44","location":"IND-DC1","last_updated":"2024-03-01","stale_asset":"no","assigned_owner":"Vikram Singh"},
    {"asset_id":"ASSET-045","asset_name":"DevProxy-IND-01","asset_type":"Proxy Server","environment":"development","owner_team":"IT Ops","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":1,"edr_installed":"no","vendor":"Squid","product":"Squid Proxy","version":"5.7","ip_address":"10.20.1.45","location":"IND-DC1","last_updated":"2023-05-01","stale_asset":"yes","assigned_owner":""},

    # === STAGING UAE — Internal ===
    {"asset_id":"ASSET-046","asset_name":"StagingApp-UAE-01","asset_type":"Application Server","environment":"staging","owner_team":"DevOps","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":2,"edr_installed":"yes","vendor":"Apache","product":"HTTP Server","version":"2.4.51","ip_address":"10.30.1.46","location":"UAE-DC2","last_updated":"2024-02-01","stale_asset":"no","assigned_owner":"Ravi Kumar"},
    {"asset_id":"ASSET-047","asset_name":"StagingApp-UAE-02","asset_type":"Application Server","environment":"staging","owner_team":"DevOps","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":2,"edr_installed":"yes","vendor":"Nginx","product":"Nginx","version":"1.23.4","ip_address":"10.30.1.47","location":"UAE-DC2","last_updated":"2024-02-01","stale_asset":"no","assigned_owner":"Ravi Kumar"},
    {"asset_id":"ASSET-048","asset_name":"StagingDB-UAE-01","asset_type":"Database Server","environment":"staging","owner_team":"Data","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":2,"edr_installed":"yes","vendor":"MySQL","product":"MySQL","version":"8.0.32","ip_address":"10.30.1.48","location":"UAE-DC2","last_updated":"2024-02-01","stale_asset":"no","assigned_owner":"Arun Nair"},
    {"asset_id":"ASSET-049","asset_name":"StagingDB-UAE-02","asset_type":"Database Server","environment":"staging","owner_team":"Data","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":2,"edr_installed":"yes","vendor":"PostgreSQL","product":"PostgreSQL","version":"15.2","ip_address":"10.30.1.49","location":"UAE-DC2","last_updated":"2024-02-01","stale_asset":"no","assigned_owner":"Arun Nair"},
    {"asset_id":"ASSET-050","asset_name":"StagingAPI-UAE-01","asset_type":"API Server","environment":"staging","owner_team":"Platform","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":2,"edr_installed":"yes","vendor":"Python","product":"FastAPI","version":"0.95.1","ip_address":"10.30.1.50","location":"UAE-DC2","last_updated":"2024-03-01","stale_asset":"no","assigned_owner":"Ravi Kumar"},
    {"asset_id":"ASSET-051","asset_name":"StagingAPI-UAE-02","asset_type":"API Server","environment":"staging","owner_team":"Platform","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":2,"edr_installed":"yes","vendor":"Node.js","product":"Express","version":"18.12.0","ip_address":"10.30.1.51","location":"UAE-DC2","last_updated":"2024-03-01","stale_asset":"no","assigned_owner":"Ravi Kumar"},
    {"asset_id":"ASSET-052","asset_name":"QATest-UAE-01","asset_type":"Test Server","environment":"staging","owner_team":"QA","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":1,"edr_installed":"yes","vendor":"Selenium","product":"Selenium Grid","version":"4.9.0","ip_address":"10.30.1.52","location":"UAE-DC2","last_updated":"2023-12-01","stale_asset":"no","assigned_owner":"Mona Al-Ali"},
    {"asset_id":"ASSET-053","asset_name":"QATest-UAE-02","asset_type":"Test Server","environment":"staging","owner_team":"QA","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":1,"edr_installed":"yes","vendor":"Selenium","product":"Selenium Grid","version":"4.9.0","ip_address":"10.30.1.53","location":"UAE-DC2","last_updated":"2023-12-01","stale_asset":"no","assigned_owner":"Mona Al-Ali"},
    {"asset_id":"ASSET-054","asset_name":"QATest-UAE-03","asset_type":"Test Server","environment":"staging","owner_team":"QA","business_service":"DevOps CI/CD Pipeline","internet_exposed":"no","criticality":1,"edr_installed":"no","vendor":"Apache","product":"HTTP Server","version":"2.4.38","ip_address":"10.30.1.54","location":"UAE-DC2","last_updated":"2022-10-01","stale_asset":"yes","assigned_owner":""},

    # === ADDITIONAL PROD ASSETS ===
    {"asset_id":"ASSET-055","asset_name":"SMSGateway-UAE-Prod-01","asset_type":"Application Server","environment":"production","owner_team":"Identity","business_service":"SMS / OTP Notification Service","internet_exposed":"yes","criticality":4,"edr_installed":"yes","vendor":"Openfire","product":"Openfire XMPP","version":"4.7.4","ip_address":"185.220.10.55","location":"UAE-DC1","last_updated":"2023-08-01","stale_asset":"no","assigned_owner":"Priya Sharma"},
    {"asset_id":"ASSET-056","asset_name":"AnalyticsSrv-UAE-Prod-01","asset_type":"Application Server","environment":"production","owner_team":"Data","business_service":"Analytics & BI Platform","internet_exposed":"no","criticality":2,"edr_installed":"yes","vendor":"Apache","product":"Spark","version":"3.3.0","ip_address":"10.10.1.56","location":"UAE-DC1","last_updated":"2024-01-01","stale_asset":"no","assigned_owner":"Arun Nair"},
    {"asset_id":"ASSET-057","asset_name":"BackupSrv-UAE-Prod-01","asset_type":"Backup Server","environment":"production","owner_team":"IT Ops","business_service":"Internal IT Services","internet_exposed":"no","criticality":4,"edr_installed":"yes","vendor":"Veeam","product":"Veeam Backup","version":"12.0","ip_address":"10.10.1.57","location":"UAE-DC1","last_updated":"2024-04-01","stale_asset":"no","assigned_owner":"Farid Al-Mansouri"},
    {"asset_id":"ASSET-058","asset_name":"KYCServer-UAE-Prod-02","asset_type":"Application Server","environment":"production","owner_team":"Compliance","business_service":"KYC / AML Processing","internet_exposed":"no","criticality":5,"edr_installed":"yes","vendor":"JetBrains","product":"TeamCity","version":"2023.05.3","ip_address":"10.10.1.58","location":"UAE-DC1","last_updated":"2023-10-01","stale_asset":"no","assigned_owner":"Layla Al-Zaabi"},
    {"asset_id":"ASSET-059","asset_name":"PrintSrv-UAE-Office-01","asset_type":"Print Server","environment":"production","owner_team":"IT Ops","business_service":"Internal IT Services","internet_exposed":"no","criticality":2,"edr_installed":"no","vendor":"Microsoft","product":"Windows Print Spooler","version":"Windows Server 2016","ip_address":"10.10.2.59","location":"UAE-OFFICE","last_updated":"2021-01-01","stale_asset":"yes","assigned_owner":""},
    {"asset_id":"ASSET-060","asset_name":"ReconSrv-UAE-Prod-01","asset_type":"Application Server","environment":"production","owner_team":"Finance","business_service":"Reconciliation Service","internet_exposed":"no","criticality":4,"edr_installed":"yes","vendor":"Oracle","product":"WebLogic","version":"12.2.1.4","ip_address":"10.10.1.60","location":"UAE-DC1","last_updated":"2023-09-01","stale_asset":"no","assigned_owner":"Nasser Al-Kaabi"},
]

# ─── 3. VULNERABILITIES (114) ──────────────────────────────────────────────
# 25 CVEs will match threat_intelligence, rest are unmatched
# Key design: top-5 risks come from internet-exposed+high-criticality+matched

kev_cves = [
    # (cve_id, cvss, description)
    ("CVE-2023-4966",  9.4, "Citrix NetScaler ADC/Gateway sensitive information disclosure - Citrix Bleed"),
    ("CVE-2024-21762", 9.6, "Fortinet FortiOS SSL VPN out-of-bound write allows remote code execution"),
    ("CVE-2024-3400",  10.0,"Palo Alto Networks PAN-OS OS command injection in GlobalProtect feature"),
    ("CVE-2021-44228", 10.0,"Apache Log4j2 JNDI remote code execution - Log4Shell"),
    ("CVE-2022-1388",  9.8, "F5 BIG-IP iControl REST unauthenticated RCE via crafted HTTP requests"),
    ("CVE-2023-20198", 10.0,"Cisco IOS XE Web UI privilege escalation via HTTP"),
    ("CVE-2023-46604", 10.0,"Apache ActiveMQ ClassInfo deserialization RCE - active ransomware use"),
    ("CVE-2022-26134", 9.8, "Atlassian Confluence OGNL injection unauthenticated RCE"),
    ("CVE-2023-42793", 9.8, "JetBrains TeamCity authentication bypass allows RCE"),
    ("CVE-2020-1472",  10.0,"Netlogon privilege escalation - Zerologon - domain compromise"),
    ("CVE-2023-28252", 7.8, "Windows Common Log File System Driver privilege escalation"),
    ("CVE-2021-26855", 9.1, "Microsoft Exchange ProxyLogon SSRF pre-auth RCE"),
    ("CVE-2023-32315", 9.8, "Ignite Realtime Openfire path traversal allows unauthenticated admin access"),
    ("CVE-2023-27350", 9.8, "PaperCut MF/NG authentication bypass allows remote code execution"),
    ("CVE-2024-1709",  10.0,"ConnectWise ScreenConnect authentication bypass - path traversal"),
    ("CVE-2023-35078", 10.0,"Ivanti Endpoint Manager Mobile authentication bypass"),
    ("CVE-2022-47966", 9.8, "ManageEngine multiple products SAML unauthenticated RCE"),
    ("CVE-2023-23397", 9.8, "Microsoft Outlook NTLM hash theft via specially crafted emails"),
    ("CVE-2022-41082", 8.8, "Microsoft Exchange Server ProxyNotShell RCE post-auth"),
    ("CVE-2021-34527", 8.8, "Windows Print Spooler RCE - PrintNightmare"),
    ("CVE-2022-30190", 7.8, "Microsoft MSDT Follina RCE via malicious Office documents"),
    ("CVE-2023-48788", 9.8, "Fortinet FortiClientEMS SQL injection allows unauthenticated RCE"),
    ("CVE-2021-27065", 7.8, "Microsoft Exchange ProxyLogon post-auth arbitrary file write"),
    ("CVE-2022-40684", 9.8, "Fortinet FortiOS/FortiProxy authentication bypass on admin interface"),
    ("CVE-2023-2868",  9.8, "Barracuda Email Security Gateway command injection - active exploitation"),
]

non_kev_cves = [
    ("CVE-2023-44487", 7.5, "HTTP/2 Rapid Reset DDoS attack vulnerability"),
    ("CVE-2022-3786",  7.5, "OpenSSL X.509 certificate verification buffer overflow"),
    ("CVE-2022-21999", 7.8, "Windows Print Spooler local privilege escalation"),
    ("CVE-2021-4034",  7.8, "Linux polkit pkexec local privilege escalation - PwnKit"),
    ("CVE-2022-0847",  7.8, "Linux kernel pipe privilege escalation - Dirty Pipe"),
    ("CVE-2021-21985", 9.8, "VMware vCenter Server RCE via vSphere Client plugin"),
    ("CVE-2022-22954", 9.8, "VMware Workspace ONE Access SSTI remote code execution"),
    ("CVE-2023-0669",  7.2, "Fortra GoAnywhere MFT authentication bypass"),
    ("CVE-2022-36537", 7.5, "ZK Framework information disclosure"),
    ("CVE-2022-24521", 7.8, "Windows CLFS driver privilege escalation"),
    ("CVE-2021-40438", 9.0, "Apache HTTP Server mod_proxy SSRF"),
    ("CVE-2022-22963", 9.8, "Spring Cloud Function SpEL code injection"),
    ("CVE-2021-3064",  9.8, "Palo Alto Networks GlobalProtect buffer overflow pre-auth RCE"),
    ("CVE-2022-26923", 8.8, "Active Directory domain escalation - certifried"),
    ("CVE-2023-24880", 5.4, "Windows SmartScreen bypass security feature bypass"),
    ("CVE-2022-34713", 7.8, "Windows MSDT RCE"),
    ("CVE-2021-36934", 7.8, "Windows SAM file local privilege escalation - HiveNightmare"),
    ("CVE-2022-30136", 9.8, "Windows Network File System RCE"),
    ("CVE-2023-21716", 9.8, "Microsoft Word RTF font table heap corruption RCE"),
    ("CVE-2022-37969", 7.8, "Windows Common Log File System Driver privilege escalation"),
    ("CVE-2022-26832", 7.5, ".NET Framework denial of service"),
    ("CVE-2022-21990", 8.8, "Remote Desktop Client RCE"),
    ("CVE-2022-24512", 6.3, ".NET Core and Visual Studio RCE"),
    ("CVE-2023-24932", 6.7, "Secure Boot security feature bypass"),
    ("CVE-2023-28229", 7.0, "Windows CNG Key Isolation Service privilege escalation"),
    ("CVE-2022-38023", 8.1, "Netlogon RPC elevation of privilege"),
    ("CVE-2022-37967", 7.2, "Windows Kerberos privilege escalation"),
    ("CVE-2022-44699", 5.5, "Windows SmartScreen security feature bypass"),
    ("CVE-2022-41076", 8.8, "PowerShell remote code execution"),
    ("CVE-2022-44710", 7.8, "DirectX graphics kernel privilege escalation"),
    ("CVE-2023-21768", 7.8, "Windows Ancillary Function Driver for WinSock privilege escalation"),
    ("CVE-2023-28231", 8.8, "Windows DHCP Server Service RCE"),
    ("CVE-2022-41033", 7.8, "Windows COM+ Event System privilege escalation"),
    ("CVE-2022-38028", 7.8, "Windows Print Spooler privilege escalation"),
    ("CVE-2022-34722", 9.8, "Windows LDAP RCE"),
    ("CVE-2022-34721", 9.8, "Windows IKE protocol extensions RCE"),
    ("CVE-2022-34718", 9.8, "Windows TCP/IP RCE"),
    ("CVE-2023-21819", 6.5, "Windows Secure Channel denial of service"),
    ("CVE-2022-44698", 5.4, "Windows SmartScreen security feature bypass"),
    ("CVE-2023-29357", 9.8, "Microsoft SharePoint Server privilege escalation"),
    ("CVE-2022-41128", 8.8, "Windows Scripting Languages RCE"),
    ("CVE-2022-41073", 7.8, "Windows Print Spooler privilege escalation"),
    ("CVE-2022-22715", 7.8, "Windows Named Pipe File System elevation of privilege"),
    ("CVE-2022-26904", 7.0, "Windows User Profile Service privilege escalation"),
    ("CVE-2022-30221", 8.8, "Windows Graphics Component RCE"),
    ("CVE-2023-21823", 7.8, "Windows Graphics Component elevation of privilege"),
    ("CVE-2023-21715", 7.3, "Microsoft Publisher security feature bypass"),
    ("CVE-2023-23376", 7.8, "Windows CLFS driver privilege escalation"),
    ("CVE-2022-41125", 7.8, "Windows CNG Key Isolation Service privilege escalation"),
    ("CVE-2022-37971", 6.1, "Microsoft Malware Protection Command and Control"),
    ("CVE-2022-38048", 7.8, "Microsoft Office remote code execution"),
    ("CVE-2022-41091", 5.4, "Windows Mark of the Web security bypass"),
    ("CVE-2023-24941", 9.8, "Windows NFS Server RCE"),
    ("CVE-2022-26809", 9.8, "Windows RPC RCE"),
    ("CVE-2022-41049", 5.4, "Windows Mark of the Web security bypass"),
    ("CVE-2022-35770", 6.5, "Windows NTLM spoofing vulnerability"),
    ("CVE-2022-37976", 8.8, "Active Directory Certificate Services privilege escalation"),
    ("CVE-2022-38034", 4.3, "Windows Workstation Service elevation of privilege"),
    ("CVE-2022-33679", 8.1, "Windows Kerberos information disclosure"),
    ("CVE-2023-28274", 7.8, "Windows Win32k privilege escalation"),
    ("CVE-2022-37975", 8.1, "Windows Group Policy privilege escalation"),
    ("CVE-2022-37977", 6.5, "Local Security Authority Subsystem Service DoS"),
    ("CVE-2022-37980", 7.8, "Windows DHCP Client privilege escalation"),
    ("CVE-2022-22040", 8.8, "Internet Information Services Dynamic Compression Module DoS"),
    ("CVE-2022-22038", 8.1, "Remote Procedure Call Runtime RCE"),
    ("CVE-2022-22037", 7.5, "Windows Advanced Local Procedure Call privilege escalation"),
    ("CVE-2022-22035", 5.9, "Windows Point-to-Point Tunneling Protocol RCE"),
    ("CVE-2022-22034", 7.8, "Windows Graphics Component privilege escalation"),
    ("CVE-2022-22029", 8.1, "Windows Network File System RCE"),
    ("CVE-2022-22028", 5.9, "Windows Network File System information disclosure"),
    ("CVE-2022-22026", 8.8, "Windows Client Server Runtime Subsystem privilege escalation"),
    ("CVE-2022-22025", 7.5, "Windows Internet Information Services information disclosure"),
    ("CVE-2022-21986", 7.5, ".NET Core denial of service"),
    ("CVE-2022-21985", 5.5, "Windows Remote Access Connection Manager information disclosure"),
    ("CVE-2022-21984", 8.8, "Windows DNS Server RCE"),
    ("CVE-2022-21983", 7.0, "Win32 Stream Enumeration privilege escalation"),
    ("CVE-2022-21981", 7.8, "Windows Common Log File System Driver privilege escalation"),
    ("CVE-2022-21979", 5.9, "Microsoft Exchange information disclosure"),
    ("CVE-2022-21978", 8.2, "Microsoft Exchange Server privilege escalation"),
    ("CVE-2022-21977", 3.3, "Media Foundation information disclosure"),
    ("CVE-2022-21975", 4.7, "Windows Hyper-V denial of service"),
]

all_cves = kev_cves + non_kev_cves[:62]  # enough to fill 114 vulnerabilities

# Asset -> CVE assignments (ensuring top-5 assets get the critical KEV CVEs)
# ASSET-001: CVE-2023-4966 (Citrix Bleed) + additional
# ASSET-003: CVE-2024-21762 (Fortinet SSL VPN) + additional  
# ASSET-007: CVE-2024-3400 (PAN-OS) + additional
# ASSET-016: CVE-2021-44228 (Log4Shell) + additional
# ASSET-005: CVE-2022-1388 (F5 BIG-IP) + additional

vuln_assignments = []
vuln_id = 1

def add_vuln(asset_id, cve_id, cvss, desc, exploit, patch, days, severity):
    vuln_assignments.append({
        "vuln_id": f"VULN-{vuln_id:03d}",
        "asset_id": asset_id,
        "cve_id": cve_id,
        "cvss_score": cvss,
        "exploit_available": exploit,
        "patch_available": patch,
        "days_open": days,
        "severity": severity,
        "description": desc,
        "first_detected": (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"),
    })

# TOP-5 RISK ASSETS — critical CVEs
add_vuln("ASSET-001","CVE-2023-4966",  9.4,"Citrix Bleed: unauthenticated session token theft on payment gateway","yes","yes",180,"critical")
add_vuln("ASSET-001","CVE-2022-26134", 9.8,"Atlassian Confluence OGNL injection found in payment gateway","yes","yes",210,"critical")
add_vuln("ASSET-002","CVE-2023-4966",  9.4,"Citrix Bleed on secondary payment gateway — load-balanced cluster","yes","yes",180,"critical")
add_vuln("ASSET-003","CVE-2024-21762", 9.6,"Fortinet SSL VPN OOB write — RCE on Identity API endpoint","yes","no", 45, "critical")
add_vuln("ASSET-003","CVE-2022-40684", 9.8,"Fortinet admin auth bypass on identity verification API","yes","yes",90, "critical")
add_vuln("ASSET-004","CVE-2024-21762", 9.6,"Fortinet SSL VPN RCE on secondary identity API","yes","no", 45, "critical")
add_vuln("ASSET-005","CVE-2022-1388",  9.8,"F5 BIG-IP iControl REST unauthenticated RCE on card processing server","yes","yes",90, "critical")
add_vuln("ASSET-005","CVE-2022-41082", 8.8,"Exchange ProxyNotShell RCE found in additional scan","yes","yes",120,"high")
add_vuln("ASSET-006","CVE-2022-1388",  9.8,"F5 BIG-IP RCE on secondary card processing server","yes","yes",90, "critical")
add_vuln("ASSET-007","CVE-2024-3400",  10.0,"PAN-OS GlobalProtect OS command injection","yes","yes",30, "critical")
add_vuln("ASSET-007","CVE-2023-20198", 10.0,"Cisco IOS XE Web UI privilege escalation found in dual-vendor stack","yes","yes",60, "critical")
add_vuln("ASSET-008","CVE-2024-3400",  10.0,"PAN-OS GlobalProtect RCE on secondary API gateway","yes","yes",30, "critical")
add_vuln("ASSET-011","CVE-2023-20198", 10.0,"Cisco IOS XE privilege escalation on VPN gateway","yes","yes",120,"critical")
add_vuln("ASSET-012","CVE-2023-20198", 10.0,"Cisco IOS XE privilege escalation on secondary VPN gateway","yes","yes",120,"critical")
add_vuln("ASSET-013","CVE-2021-26855", 9.1,"Exchange ProxyLogon SSRF — email gateway pre-auth RCE","yes","yes",540,"critical")
add_vuln("ASSET-013","CVE-2021-27065", 7.8,"Exchange ProxyLogon file write post-auth — chained with ProxyLogon","yes","yes",540,"high")
add_vuln("ASSET-016","CVE-2021-44228", 10.0,"Log4Shell RCE on fraud detection engine — unpatched since 2021","yes","no", 890,"critical")
add_vuln("ASSET-016","CVE-2023-28252", 7.8,"Windows CLFS driver privilege escalation on fraud engine","yes","yes",60, "high")
add_vuln("ASSET-017","CVE-2021-44228", 10.0,"Log4Shell on secondary fraud detection engine — same unpatched version","yes","no", 890,"critical")
add_vuln("ASSET-018","CVE-2022-38023", 8.1,"Netlogon RPC elevation on core database server","yes","yes",90, "high")
add_vuln("ASSET-019","CVE-2022-38023", 8.1,"Netlogon RPC elevation on secondary database server","yes","yes",90, "high")
add_vuln("ASSET-020","CVE-2023-42793", 9.8,"JetBrains TeamCity auth bypass allows build pipeline compromise","yes","yes",60, "critical")
add_vuln("ASSET-021","CVE-2022-21984", 8.8,"Windows DNS Server RCE on settlement server","yes","yes",120,"high")
add_vuln("ASSET-023","CVE-2020-1472",  10.0,"Zerologon domain controller compromise via Netlogon","yes","yes",180,"critical")
add_vuln("ASSET-024","CVE-2020-1472",  10.0,"Zerologon on secondary domain controller","yes","yes",180,"critical")
add_vuln("ASSET-025","CVE-2023-44487", 7.5,"HTTP/2 Rapid Reset DDoS on transaction monitoring","yes","yes",30, "high")
add_vuln("ASSET-029","CVE-2022-47966", 9.8,"ManageEngine SAML unauthenticated RCE — compliance server stale","yes","yes",360,"critical")
add_vuln("ASSET-031","CVE-2023-42793", 9.8,"JetBrains TeamCity auth bypass on dev app server","yes","yes",60, "critical")
add_vuln("ASSET-032","CVE-2022-22963", 9.8,"Spring Cloud Function SpEL injection on Jenkins build server","yes","yes",180,"critical")
add_vuln("ASSET-033","CVE-2022-0847",  7.8,"Dirty Pipe Linux kernel privilege escalation on dev DB","yes","yes",300,"high")
add_vuln("ASSET-035","CVE-2022-26904", 7.0,"Windows User Profile Service privilege escalation on GitLab server","yes","yes",180,"high")
add_vuln("ASSET-036","CVE-2022-21975", 4.7,"Windows Hyper-V DoS on stale test server","no", "yes",540,"medium")
add_vuln("ASSET-037","CVE-2022-21979", 5.9,"Exchange information disclosure on stale test server","no", "yes",540,"medium")
add_vuln("ASSET-039","CVE-2021-44228", 10.0,"Log4Shell on dev app server — same unpatched binary as prod","yes","no", 890,"critical")
add_vuln("ASSET-040","CVE-2022-26134", 9.8,"Confluence OGNL injection on dev tools server","yes","yes",210,"critical")
add_vuln("ASSET-055","CVE-2023-32315", 9.8,"Openfire XMPP path traversal — SMS gateway unauthenticated admin access","yes","yes",90, "critical")
add_vuln("ASSET-058","CVE-2023-42793", 9.8,"JetBrains TeamCity auth bypass on secondary KYC server","yes","yes",60, "critical")
add_vuln("ASSET-059","CVE-2021-34527", 8.8,"PrintNightmare RCE on stale print server — unpatched since 2021","yes","yes",900,"high")
add_vuln("ASSET-060","CVE-2022-21978", 8.2,"Exchange Server privilege escalation on reconciliation server","yes","yes",120,"high")

# Fill remaining vulns with non-KEV CVEs distributed across more assets
extra_assignments = [
    ("ASSET-009", "CVE-2023-44487", 7.5, "HTTP/2 Rapid Reset DDoS vulnerability on web load balancer", "yes", "yes", 30),
    ("ASSET-010", "CVE-2023-44487", 7.5, "HTTP/2 Rapid Reset DDoS vulnerability on secondary load balancer", "yes", "yes", 30),
    ("ASSET-014", "CVE-2022-3786",  7.5, "OpenSSL buffer overflow on web portal server", "no",  "yes", 120),
    ("ASSET-015", "CVE-2022-3786",  7.5, "OpenSSL buffer overflow on secondary web portal", "no",  "yes", 120),
    ("ASSET-022", "CVE-2022-22029", 8.1, "Windows NFS Server RCE on settlement server 02", "yes", "yes", 90),
    ("ASSET-026", "CVE-2022-24521", 7.8, "Windows CLFS privilege escalation on SIEM", "yes", "yes", 60),
    ("ASSET-027", "CVE-2021-4034",  7.8, "Linux polkit pkexec privilege escalation on app server", "yes", "yes", 400),
    ("ASSET-028", "CVE-2021-4034",  7.8, "Linux polkit pkexec on secondary app server", "yes", "yes", 400),
    ("ASSET-030", "CVE-2022-36537", 7.5, "ZK Framework information disclosure on log server", "yes", "yes", 180),
    ("ASSET-034", "CVE-2022-0847",  7.8, "Dirty Pipe Linux kernel LPE on dev postgres server", "yes", "yes", 300),
    ("ASSET-038", "CVE-2022-22963", 9.8, "Spring Cloud SpEL injection on dev API server", "yes", "yes", 180),
    ("ASSET-041", "CVE-2022-0669",  7.2, "GoAnywhere authentication bypass on Jira server", "yes", "yes", 120),
    ("ASSET-042", "CVE-2023-24880", 5.4, "SmartScreen bypass on dev monitor server", "no",  "yes", 60),
    ("ASSET-043", "CVE-2022-34713", 7.8, "Windows MSDT RCE on security scanner", "yes", "yes", 90),
    ("ASSET-044", "CVE-2022-21975", 4.7, "Hyper-V DoS on Docker container host", "no",  "yes", 120),
    ("ASSET-045", "CVE-2022-21979", 5.9, "Exchange information disclosure on dev proxy", "no",  "yes", 540),
    ("ASSET-046", "CVE-2023-24932", 6.7, "Secure Boot bypass on staging app server", "no",  "yes", 60),
    ("ASSET-047", "CVE-2022-22715", 7.8, "Named Pipe File System LPE on staging nginx", "yes", "yes", 120),
    ("ASSET-048", "CVE-2022-21981", 7.8, "CLFS driver LPE on staging DB server", "yes", "yes", 90),
    ("ASSET-049", "CVE-2022-22026", 8.8, "CSRSS LPE on staging postgres server", "yes", "yes", 90),
    ("ASSET-050", "CVE-2022-21984", 8.8, "Windows DNS RCE on staging API server", "yes", "yes", 120),
    ("ASSET-051", "CVE-2022-22034", 7.8, "Windows Graphics Component LPE on staging API", "yes", "yes", 120),
    ("ASSET-052", "CVE-2022-21990", 8.8, "Remote Desktop Client RCE on QA test server", "yes", "yes", 180),
    ("ASSET-053", "CVE-2022-34722", 9.8, "Windows LDAP RCE on QA test server 02", "yes", "yes", 180),
    ("ASSET-054", "CVE-2022-34718", 9.8, "Windows TCP/IP RCE on stale QA test server", "yes", "yes", 540),
    ("ASSET-056", "CVE-2022-22038", 8.1, "RPC Runtime RCE on analytics server", "yes", "yes", 90),
    ("ASSET-057", "CVE-2022-22037", 7.5, "ALPC LPE on backup server", "yes", "yes", 60),
    ("ASSET-059", "CVE-2022-38028", 7.8, "Print Spooler LPE on stale print server (additional)", "yes", "yes", 500),
    ("ASSET-009", "CVE-2022-21999", 7.8, "Windows Print Spooler LPE on load balancer", "yes", "yes", 300),
    ("ASSET-023", "CVE-2022-26923", 8.8, "Active Directory certifried domain escalation on DC01", "yes", "yes", 120),
    ("ASSET-024", "CVE-2022-26923", 8.8, "Active Directory certifried domain escalation on DC02", "yes", "yes", 120),
    ("ASSET-025", "CVE-2022-37969", 7.8, "CLFS privilege escalation on transaction monitor", "yes", "yes", 90),
    ("ASSET-016", "CVE-2022-30190", 7.8, "Follina MSDT RCE on fraud engine — layered attack surface", "yes", "yes", 360),
    ("ASSET-017", "CVE-2022-30190", 7.8, "Follina MSDT RCE on secondary fraud engine", "yes", "yes", 360),
    ("ASSET-001", "CVE-2023-23397", 9.8, "Outlook NTLM hash theft via crafted email — discovered in prod scan", "yes", "yes", 120),
    ("ASSET-003", "CVE-2023-23397", 9.8, "Outlook NTLM hash theft targeting identity API team endpoints", "yes", "yes", 120),
    ("ASSET-018", "CVE-2022-37977", 6.5, "LSASS denial of service on core DB server", "no", "yes", 60),
    ("ASSET-019", "CVE-2022-37977", 6.5, "LSASS DoS on secondary core DB server", "no", "yes", 60),
    ("ASSET-026", "CVE-2022-41125", 7.8, "CNG Key Isolation Service LPE on SIEM", "yes", "yes", 90),
    ("ASSET-027", "CVE-2022-22040", 8.8, "IIS Dynamic Compression DoS on mobile app server", "yes", "yes", 60),
    ("ASSET-028", "CVE-2022-22035", 5.9, "PPTP protocol RCE on mobile app server 02", "yes", "yes", 90),
    ("ASSET-060", "CVE-2022-21977", 3.3, "Media Foundation information disclosure on recon server", "no", "yes", 60),
    ("ASSET-007", "CVE-2022-22029", 8.1, "NFS Server RCE on API gateway 01 — additional vuln", "yes", "yes", 60),
    ("ASSET-008", "CVE-2022-21984", 8.8, "DNS Server RCE on API gateway 02", "yes", "yes", 60),
    ("ASSET-011", "CVE-2022-26809", 9.8, "Windows RPC RCE on VPN gateway 01", "yes", "yes", 180),
    ("ASSET-012", "CVE-2022-26809", 9.8, "Windows RPC RCE on VPN gateway 02", "yes", "yes", 180),
    ("ASSET-029", "CVE-2023-2868",  9.8, "Barracuda ESG command injection on compliance server", "yes", "yes", 240),
    ("ASSET-020", "CVE-2022-47966", 9.8, "ManageEngine SAML RCE on KYC server — additional tool installed", "yes", "yes", 180),
    ("ASSET-055", "CVE-2023-27350", 9.8, "PaperCut auth bypass — SMS gateway runs PaperCut for PDF billing", "yes", "yes", 60),
    ("ASSET-013", "CVE-2022-41082", 8.8, "Exchange ProxyNotShell on email gateway", "yes", "yes", 240),
    ("ASSET-014", "CVE-2022-22054", 7.8, "Windows Error Reporting LPE on portal server", "no", "yes", 90),
    ("ASSET-031", "CVE-2023-48788", 9.8, "Fortinet EMS SQL injection — dev app has FortiClient EMS connector", "yes", "yes", 60),
    ("ASSET-022", "CVE-2022-37975", 8.1, "Group Policy privilege escalation on settlement server 02", "yes", "yes", 180),
    ("ASSET-021", "CVE-2022-37980", 7.8, "DHCP Client LPE on settlement server 01", "yes", "yes", 120),
    ("ASSET-032", "CVE-2022-30221", 8.8, "Windows Graphics Component RCE on Jenkins build server", "yes", "yes", 180),
    ("ASSET-033", "CVE-2022-38034", 4.3, "Workstation Service LPE on dev DB 01", "no", "yes", 120),
    ("ASSET-034", "CVE-2022-33679", 8.1, "Kerberos info disclosure on dev postgres server", "no", "yes", 120),
    ("ASSET-040", "CVE-2022-24512", 6.3, ".NET RCE on Confluence dev tools", "yes", "yes", 180),
    ("ASSET-041", "CVE-2022-21985", 5.5, "Remote Access Mgr info disclosure on Jira server", "no", "yes", 60),
    ("ASSET-035", "CVE-2022-41128", 8.8, "Windows Scripting Languages RCE on GitLab server", "yes", "yes", 120),
    ("ASSET-058", "CVE-2022-47966", 9.8, "ManageEngine SAML RCE on secondary KYC server", "yes", "yes", 180),
    ("ASSET-060", "CVE-2022-41033", 7.8, "COM+ Event System LPE on recon server", "yes", "yes", 90),
    ("ASSET-056", "CVE-2022-26832", 7.5, ".NET Framework DoS on analytics server", "no", "yes", 60),
    ("ASSET-057", "CVE-2022-44699", 5.5, "SmartScreen bypass on backup server", "no", "yes", 90),
    ("ASSET-046", "CVE-2022-44710", 7.8, "DirectX graphics kernel LPE on staging app 01", "yes", "yes", 60),
    ("ASSET-047", "CVE-2022-41049", 5.4, "Mark of the Web bypass on staging nginx", "no", "yes", 90),
    ("ASSET-048", "CVE-2023-24941", 9.8, "Windows NFS Server RCE on staging DB 01", "yes", "yes", 90),
    ("ASSET-049", "CVE-2023-28231", 8.8, "Windows DHCP Server RCE on staging DB 02", "yes", "yes", 90),
    ("ASSET-050", "CVE-2022-35770", 6.5, "NTLM spoofing on staging API 01", "no", "yes", 60),
    ("ASSET-051", "CVE-2022-37976", 8.8, "AD CS privilege escalation on staging API 02", "yes", "yes", 90),
    ("ASSET-052", "CVE-2022-41073", 7.8, "Print Spooler LPE on QA test server 01", "yes", "yes", 120),
    ("ASSET-053", "CVE-2023-21768", 7.8, "AFDSYS privilege escalation on QA test server 02", "yes", "yes", 90),
    ("ASSET-002", "CVE-2023-23397", 9.8, "Outlook NTLM hash theft on payment gateway 02", "yes", "yes", 120),
    ("ASSET-004", "CVE-2022-40684", 9.8, "Fortinet admin auth bypass on identity API 02", "yes", "yes", 90),
]

for i, (aid, cid, cvss, desc, exploit, patch, days) in enumerate(extra_assignments):
    sev = "critical" if cvss >= 9.0 else ("high" if cvss >= 7.0 else "medium")
    vuln_id += 1
    add_vuln(aid, cid, cvss, desc, exploit, patch, days, sev)
    vuln_id -= 1  # will be incremented below

# Finalize vuln IDs
vulns = []
for i, v in enumerate(vuln_assignments):
    v2 = dict(v)
    v2["vuln_id"] = f"VULN-{i+1:03d}"
    vulns.append(v2)

# Pad to exactly 114 if needed
print(f"Generated {len(vulns)} vulnerabilities (target: 114)")

# ─── 4. THREAT INTELLIGENCE (40) ───────────────────────────────────────────
# 25 matching CVEs, 15 noise CVEs not in our vulnerability list

matching_ti = [
    {"threat_id":"TI-001","campaign_name":"GulfStrike","threat_actor":"UNC4841","cve_id":"CVE-2023-4966","attack_type":"Ransomware","target_sector":"Financial Services","target_region":"Gulf Cooperation Council","first_seen":"2024-01-10","last_seen":"2024-04-10","confidence_level":"high","ioc_count":47,"ttp_count":12},
    {"threat_id":"TI-002","campaign_name":"BlackMint","threat_actor":"Scattered Spider","cve_id":"CVE-2024-21762","attack_type":"Ransomware","target_sector":"FinTech","target_region":"Middle East","first_seen":"2024-02-01","last_seen":"2024-04-12","confidence_level":"high","ioc_count":33,"ttp_count":9},
    {"threat_id":"TI-003","campaign_name":"DarkNexus","threat_actor":"Lazarus Group","cve_id":"CVE-2024-3400","attack_type":"Espionage/Ransomware","target_sector":"Payment Processing","target_region":"UAE,KSA","first_seen":"2024-03-01","last_seen":"2024-04-15","confidence_level":"high","ioc_count":28,"ttp_count":15},
    {"threat_id":"TI-004","campaign_name":"GulfStrike","threat_actor":"UNC4841","cve_id":"CVE-2021-44228","attack_type":"Ransomware","target_sector":"Financial Services","target_region":"Gulf Cooperation Council","first_seen":"2022-01-05","last_seen":"2024-04-10","confidence_level":"high","ioc_count":156,"ttp_count":20},
    {"threat_id":"TI-005","campaign_name":"BlackMint","threat_actor":"Scattered Spider","cve_id":"CVE-2022-1388","attack_type":"Ransomware","target_sector":"FinTech","target_region":"Middle East","first_seen":"2022-10-01","last_seen":"2024-04-12","confidence_level":"high","ioc_count":41,"ttp_count":11},
    {"threat_id":"TI-006","campaign_name":"OperationSilverFox","threat_actor":"APT33","cve_id":"CVE-2023-20198","attack_type":"Espionage","target_sector":"Financial Services","target_region":"UAE","first_seen":"2023-10-20","last_seen":"2024-03-30","confidence_level":"medium","ioc_count":22,"ttp_count":8},
    {"threat_id":"TI-007","campaign_name":"GulfStrike","threat_actor":"UNC4841","cve_id":"CVE-2023-46604","attack_type":"Ransomware","target_sector":"Financial Services","target_region":"Gulf Cooperation Council","first_seen":"2023-11-01","last_seen":"2024-04-10","confidence_level":"high","ioc_count":39,"ttp_count":13},
    {"threat_id":"TI-008","campaign_name":"OperationSilverFox","threat_actor":"APT33","cve_id":"CVE-2022-26134","attack_type":"Espionage","target_sector":"Banking","target_region":"Middle East","first_seen":"2022-06-15","last_seen":"2024-02-28","confidence_level":"medium","ioc_count":18,"ttp_count":7},
    {"threat_id":"TI-009","campaign_name":"BlackMint","threat_actor":"Scattered Spider","cve_id":"CVE-2023-42793","attack_type":"Ransomware","target_sector":"FinTech","target_region":"GCC,India","first_seen":"2023-09-01","last_seen":"2024-04-12","confidence_level":"high","ioc_count":52,"ttp_count":14},
    {"threat_id":"TI-010","campaign_name":"GulfStrike","threat_actor":"UNC4841","cve_id":"CVE-2020-1472","attack_type":"Ransomware","target_sector":"Financial Services","target_region":"Gulf Cooperation Council","first_seen":"2020-09-01","last_seen":"2024-04-10","confidence_level":"high","ioc_count":89,"ttp_count":18},
    {"threat_id":"TI-011","campaign_name":"DarkNexus","threat_actor":"Lazarus Group","cve_id":"CVE-2023-28252","attack_type":"Espionage/Ransomware","target_sector":"Payment Processing","target_region":"UAE,KSA","first_seen":"2023-04-01","last_seen":"2024-04-15","confidence_level":"medium","ioc_count":16,"ttp_count":6},
    {"threat_id":"TI-012","campaign_name":"OperationSilverFox","threat_actor":"APT33","cve_id":"CVE-2021-26855","attack_type":"Espionage","target_sector":"Financial Services","target_region":"Gulf","first_seen":"2021-03-10","last_seen":"2024-01-20","confidence_level":"medium","ioc_count":34,"ttp_count":10},
    {"threat_id":"TI-013","campaign_name":"GulfStrike","threat_actor":"UNC4841","cve_id":"CVE-2023-32315","attack_type":"Ransomware","target_sector":"FinTech","target_region":"GCC","first_seen":"2023-06-01","last_seen":"2024-03-15","confidence_level":"medium","ioc_count":12,"ttp_count":5},
    {"threat_id":"TI-014","campaign_name":"BlackMint","threat_actor":"Scattered Spider","cve_id":"CVE-2023-27350","attack_type":"Ransomware","target_sector":"Financial Services","target_region":"Middle East","first_seen":"2023-04-15","last_seen":"2024-04-12","confidence_level":"high","ioc_count":27,"ttp_count":9},
    {"threat_id":"TI-015","campaign_name":"DarkNexus","threat_actor":"Lazarus Group","cve_id":"CVE-2024-1709","attack_type":"Espionage/Ransomware","target_sector":"Payment Processing","target_region":"UAE,India","first_seen":"2024-02-20","last_seen":"2024-04-15","confidence_level":"high","ioc_count":19,"ttp_count":7},
    {"threat_id":"TI-016","campaign_name":"OperationSilverFox","threat_actor":"APT33","cve_id":"CVE-2023-35078","attack_type":"Espionage","target_sector":"Financial Services","target_region":"UAE","first_seen":"2023-07-25","last_seen":"2024-02-10","confidence_level":"medium","ioc_count":14,"ttp_count":6},
    {"threat_id":"TI-017","campaign_name":"GulfStrike","threat_actor":"UNC4841","cve_id":"CVE-2022-47966","attack_type":"Ransomware","target_sector":"FinTech","target_region":"Gulf Cooperation Council","first_seen":"2023-01-20","last_seen":"2024-04-10","confidence_level":"high","ioc_count":31,"ttp_count":10},
    {"threat_id":"TI-018","campaign_name":"BlackMint","threat_actor":"Scattered Spider","cve_id":"CVE-2023-23397","attack_type":"Ransomware","target_sector":"Financial Services","target_region":"Middle East,GCC","first_seen":"2023-03-20","last_seen":"2024-04-12","confidence_level":"high","ioc_count":43,"ttp_count":11},
    {"threat_id":"TI-019","campaign_name":"DarkNexus","threat_actor":"Lazarus Group","cve_id":"CVE-2022-41082","attack_type":"Espionage/Ransomware","target_sector":"Payment Processing","target_region":"UAE","first_seen":"2022-10-05","last_seen":"2024-04-15","confidence_level":"medium","ioc_count":22,"ttp_count":8},
    {"threat_id":"TI-020","campaign_name":"OperationSilverFox","threat_actor":"APT33","cve_id":"CVE-2021-34527","attack_type":"Espionage","target_sector":"Financial Services","target_region":"Gulf","first_seen":"2021-07-05","last_seen":"2023-12-01","confidence_level":"low","ioc_count":8,"ttp_count":4},
    {"threat_id":"TI-021","campaign_name":"GulfStrike","threat_actor":"UNC4841","cve_id":"CVE-2022-30190","attack_type":"Ransomware","target_sector":"Financial Services","target_region":"GCC","first_seen":"2022-06-01","last_seen":"2024-04-10","confidence_level":"medium","ioc_count":24,"ttp_count":8},
    {"threat_id":"TI-022","campaign_name":"BlackMint","threat_actor":"Scattered Spider","cve_id":"CVE-2023-48788","attack_type":"Ransomware","target_sector":"FinTech","target_region":"Middle East","first_seen":"2024-01-15","last_seen":"2024-04-12","confidence_level":"high","ioc_count":17,"ttp_count":6},
    {"threat_id":"TI-023","campaign_name":"DarkNexus","threat_actor":"Lazarus Group","cve_id":"CVE-2021-27065","attack_type":"Espionage","target_sector":"Payment Processing","target_region":"UAE","first_seen":"2021-03-15","last_seen":"2024-02-10","confidence_level":"medium","ioc_count":11,"ttp_count":5},
    {"threat_id":"TI-024","campaign_name":"GulfStrike","threat_actor":"UNC4841","cve_id":"CVE-2022-40684","attack_type":"Ransomware","target_sector":"Financial Services","target_region":"GCC","first_seen":"2022-10-10","last_seen":"2024-04-10","confidence_level":"high","ioc_count":35,"ttp_count":10},
    {"threat_id":"TI-025","campaign_name":"OperationSilverFox","threat_actor":"APT33","cve_id":"CVE-2023-2868","attack_type":"Espionage","target_sector":"Financial Services","target_region":"Middle East","first_seen":"2023-05-25","last_seen":"2024-01-10","confidence_level":"medium","ioc_count":9,"ttp_count":4},
]

# 15 noise records — CVEs NOT present in vulnerabilities.csv
noise_ti = [
    {"threat_id":"TI-026","campaign_name":"SandstormOps","threat_actor":"APT34","cve_id":"CVE-2024-26169","attack_type":"Espionage","target_sector":"Energy","target_region":"Middle East","first_seen":"2024-03-01","last_seen":"2024-04-01","confidence_level":"low","ioc_count":5,"ttp_count":3},
    {"threat_id":"TI-027","campaign_name":"SandstormOps","threat_actor":"APT34","cve_id":"CVE-2024-21893","attack_type":"Espionage","target_sector":"Telecom","target_region":"UAE","first_seen":"2024-02-15","last_seen":"2024-03-20","confidence_level":"low","ioc_count":7,"ttp_count":3},
    {"threat_id":"TI-028","campaign_name":"NightViper","threat_actor":"TA453","cve_id":"CVE-2024-27198","attack_type":"Phishing","target_sector":"Financial Services","target_region":"Global","first_seen":"2024-03-10","last_seen":"2024-04-08","confidence_level":"medium","ioc_count":12,"ttp_count":5},
    {"threat_id":"TI-029","campaign_name":"NightViper","threat_actor":"TA453","cve_id":"CVE-2024-27199","attack_type":"Phishing","target_sector":"Financial Services","target_region":"Global","first_seen":"2024-03-10","last_seen":"2024-04-08","confidence_level":"medium","ioc_count":11,"ttp_count":5},
    {"threat_id":"TI-030","campaign_name":"CobaltMirage","threat_actor":"Charming Kitten","cve_id":"CVE-2023-34960","attack_type":"Ransomware","target_sector":"Banking","target_region":"Iran,UAE","first_seen":"2023-11-01","last_seen":"2024-02-28","confidence_level":"medium","ioc_count":15,"ttp_count":6},
    {"threat_id":"TI-031","campaign_name":"CobaltMirage","threat_actor":"Charming Kitten","cve_id":"CVE-2024-0519","attack_type":"Browser Exploit","target_sector":"Financial","target_region":"Global","first_seen":"2024-01-20","last_seen":"2024-03-10","confidence_level":"high","ioc_count":8,"ttp_count":4},
    {"threat_id":"TI-032","campaign_name":"DesertFalcon","threat_actor":"StrongPity","cve_id":"CVE-2024-20253","attack_type":"Espionage","target_sector":"Government","target_region":"Gulf","first_seen":"2024-02-01","last_seen":"2024-04-05","confidence_level":"low","ioc_count":6,"ttp_count":3},
    {"threat_id":"TI-033","campaign_name":"DesertFalcon","threat_actor":"StrongPity","cve_id":"CVE-2024-22024","attack_type":"Espionage","target_sector":"Defense","target_region":"UAE,KSA","first_seen":"2024-01-25","last_seen":"2024-03-15","confidence_level":"low","ioc_count":4,"ttp_count":2},
    {"threat_id":"TI-034","campaign_name":"PhoenixClaw","threat_actor":"TA505","cve_id":"CVE-2024-21888","attack_type":"Ransomware","target_sector":"Retail,FinTech","target_region":"Global","first_seen":"2024-02-05","last_seen":"2024-04-15","confidence_level":"medium","ioc_count":19,"ttp_count":7},
    {"threat_id":"TI-035","campaign_name":"PhoenixClaw","threat_actor":"TA505","cve_id":"CVE-2024-26230","attack_type":"Ransomware","target_sector":"Financial Services","target_region":"Europe,MENA","first_seen":"2024-03-05","last_seen":"2024-04-15","confidence_level":"medium","ioc_count":14,"ttp_count":6},
    {"threat_id":"TI-036","campaign_name":"SilverThread","threat_actor":"Volt Typhoon","cve_id":"CVE-2024-28252","attack_type":"Espionage","target_sector":"Critical Infrastructure","target_region":"US,MENA","first_seen":"2024-03-20","last_seen":"2024-04-10","confidence_level":"low","ioc_count":3,"ttp_count":2},
    {"threat_id":"TI-037","campaign_name":"SilverThread","threat_actor":"Volt Typhoon","cve_id":"CVE-2024-29943","attack_type":"Espionage","target_sector":"Telecom","target_region":"Global","first_seen":"2024-03-25","last_seen":"2024-04-12","confidence_level":"low","ioc_count":2,"ttp_count":1},
    {"threat_id":"TI-038","campaign_name":"StormCastle","threat_actor":"Storm-0978","cve_id":"CVE-2024-30040","attack_type":"Ransomware","target_sector":"Financial Services","target_region":"Europe,MENA","first_seen":"2024-04-01","last_seen":"2024-04-14","confidence_level":"medium","ioc_count":9,"ttp_count":4},
    {"threat_id":"TI-039","campaign_name":"StormCastle","threat_actor":"Storm-0978","cve_id":"CVE-2024-30051","attack_type":"Ransomware","target_sector":"Banking","target_region":"Global","first_seen":"2024-04-01","last_seen":"2024-04-14","confidence_level":"medium","ioc_count":11,"ttp_count":5},
    {"threat_id":"TI-040","campaign_name":"GhostMarket","threat_actor":"FIN7","cve_id":"CVE-2023-46805","attack_type":"Financial Crime","target_sector":"Payment Processing","target_region":"Global","first_seen":"2024-01-10","last_seen":"2024-03-31","confidence_level":"high","ioc_count":25,"ttp_count":9},
]

threat_intel = matching_ti + noise_ti

# ─── 5. REMEDIATION GUIDANCE (30) ──────────────────────────────────────────
remediation = [
    {"id":"REM-001","cve_id":"CVE-2023-4966","nist_control_id":"SI-2","control_family":"System and Information Integrity","remediation_hint":"Apply Citrix hotfix CTX579459 immediately; terminate all active sessions; rotate session tokens","priority":"critical","effort_days":1},
    {"id":"REM-002","cve_id":"CVE-2024-21762","nist_control_id":"SI-2","control_family":"System and Information Integrity","remediation_hint":"Upgrade FortiOS to 7.4.2+ or disable SSL VPN; apply Fortinet advisory FG-IR-24-015","priority":"critical","effort_days":2},
    {"id":"REM-003","cve_id":"CVE-2024-3400","nist_control_id":"SI-2","control_family":"System and Information Integrity","remediation_hint":"Apply PAN-OS patch; enable Threat Prevention subscription; check for compromise using Palo Alto indicators","priority":"critical","effort_days":1},
    {"id":"REM-004","cve_id":"CVE-2021-44228","nist_control_id":"SI-2","control_family":"System and Information Integrity","remediation_hint":"Upgrade Log4j to 2.17.1+; set LOG4J_FORMAT_MSG_NO_LOOKUPS=true as interim; audit all Java applications","priority":"critical","effort_days":3},
    {"id":"REM-005","cve_id":"CVE-2022-1388","nist_control_id":"SI-2","control_family":"System and Information Integrity","remediation_hint":"Apply F5 BIG-IP security patch K23605346; block iControl REST access from untrusted networks","priority":"critical","effort_days":1},
    {"id":"REM-006","cve_id":"CVE-2023-20198","nist_control_id":"SI-2","control_family":"System and Information Integrity","remediation_hint":"Disable HTTP server feature on all internet-facing IOS XE; apply Cisco advisory cisco-sa-iosxe-webui-privesc","priority":"critical","effort_days":1},
    {"id":"REM-007","cve_id":"CVE-2023-46604","nist_control_id":"RA-5","control_family":"Risk Assessment","remediation_hint":"Upgrade ActiveMQ to 5.15.16+, 5.16.7+, 5.17.6+, or 5.18.3+; block port 61616 externally","priority":"critical","effort_days":1},
    {"id":"REM-008","cve_id":"CVE-2022-26134","nist_control_id":"SI-2","control_family":"System and Information Integrity","remediation_hint":"Upgrade Confluence to patched version; restrict access to Confluence; check for webshells post-patch","priority":"critical","effort_days":2},
    {"id":"REM-009","cve_id":"CVE-2023-42793","nist_control_id":"SA-22","control_family":"System and Services Acquisition","remediation_hint":"Upgrade TeamCity to 2023.05.4+; disable guest login; rotate all build tokens and service accounts","priority":"critical","effort_days":2},
    {"id":"REM-010","cve_id":"CVE-2020-1472","nist_control_id":"AC-2","control_family":"Access Control","remediation_hint":"Apply Microsoft KB4557222; enforce secure channel signing; monitor Netlogon event 5829 for legacy clients","priority":"critical","effort_days":1},
    {"id":"REM-011","cve_id":"CVE-2023-28252","nist_control_id":"SI-2","control_family":"System and Information Integrity","remediation_hint":"Apply April 2023 Patch Tuesday cumulative update; monitor for CLFS driver exploit activity","priority":"high","effort_days":3},
    {"id":"REM-012","cve_id":"CVE-2021-26855","nist_control_id":"IR-4","control_family":"Incident Response","remediation_hint":"Apply Exchange CU and patch; run MSERT scanner; check for webshells in OWA directories","priority":"critical","effort_days":1},
    {"id":"REM-013","cve_id":"CVE-2023-32315","nist_control_id":"SI-2","control_family":"System and Information Integrity","remediation_hint":"Upgrade Openfire to 4.7.5+ or 4.6.8+; block admin console from internet; reset all admin credentials","priority":"critical","effort_days":1},
    {"id":"REM-014","cve_id":"CVE-2023-27350","nist_control_id":"RA-5","control_family":"Risk Assessment","remediation_hint":"Apply PaperCut patch; enable allowlist for server IP; review print logs for anomalous commands","priority":"critical","effort_days":1},
    {"id":"REM-015","cve_id":"CVE-2024-1709","nist_control_id":"SI-2","control_family":"System and Information Integrity","remediation_hint":"Apply ConnectWise ScreenConnect update; enforce MFA; audit remote session logs immediately","priority":"critical","effort_days":1},
    {"id":"REM-016","cve_id":"CVE-2023-35078","nist_control_id":"IR-4","control_family":"Incident Response","remediation_hint":"Apply Ivanti EPMM patch; assume compromise if unpatched; reset all user credentials and review API logs","priority":"critical","effort_days":1},
    {"id":"REM-017","cve_id":"CVE-2022-47966","nist_control_id":"SA-22","control_family":"System and Services Acquisition","remediation_hint":"Upgrade ManageEngine product; rotate SAML certificates; audit authentication logs for pre-patch access","priority":"critical","effort_days":2},
    {"id":"REM-018","cve_id":"CVE-2023-23397","nist_control_id":"AC-2","control_family":"Access Control","remediation_hint":"Apply Microsoft security update; block outbound SMB (445); add Protected Users security group members","priority":"high","effort_days":2},
    {"id":"REM-019","cve_id":"CVE-2022-41082","nist_control_id":"SI-2","control_family":"System and Information Integrity","remediation_hint":"Apply Exchange November 2022 SU; use EMS URL rewrite mitigation if immediate patching not possible","priority":"high","effort_days":2},
    {"id":"REM-020","cve_id":"CVE-2021-34527","nist_control_id":"SA-22","control_family":"System and Services Acquisition","remediation_hint":"Disable Print Spooler service on non-print servers; apply KB5005010; restrict Point and Print policy","priority":"high","effort_days":1},
    {"id":"REM-021","cve_id":"CVE-2022-30190","nist_control_id":"IR-4","control_family":"Incident Response","remediation_hint":"Disable MSDT URL protocol; apply Microsoft patch; block .diagcab files at email gateway","priority":"high","effort_days":1},
    {"id":"REM-022","cve_id":"CVE-2023-48788","nist_control_id":"RA-5","control_family":"Risk Assessment","remediation_hint":"Upgrade FortiClientEMS; restrict EMS access to internal networks only; review SQL Server audit logs","priority":"critical","effort_days":2},
    {"id":"REM-023","cve_id":"CVE-2021-27065","nist_control_id":"IR-4","control_family":"Incident Response","remediation_hint":"Apply Exchange patch; scan for webshells; run Microsoft MSERT; check OWA and ECP directories","priority":"high","effort_days":1},
    {"id":"REM-024","cve_id":"CVE-2022-40684","nist_control_id":"AC-2","control_family":"Access Control","remediation_hint":"Apply Fortinet patch; restrict admin interface to trusted IPs; review admin API access logs","priority":"critical","effort_days":1},
    {"id":"REM-025","cve_id":"CVE-2023-2868","nist_control_id":"SA-22","control_family":"System and Services Acquisition","remediation_hint":"Replace affected ESG hardware (Barracuda-mandated); do not simply patch; treat as assumed breach","priority":"critical","effort_days":5},
    {"id":"REM-026","cve_id":"CVE-2022-26809","nist_control_id":"SC-7","control_family":"System and Communications Protection","remediation_hint":"Apply Windows RPC patch KB5012170; block TCP port 445 at perimeter; restrict RPC to trusted segments","priority":"high","effort_days":1},
    {"id":"REM-027","cve_id":"CVE-2022-38023","nist_control_id":"AC-2","control_family":"Access Control","remediation_hint":"Apply Windows Netlogon patch; enforce secure RPC; monitor event IDs 5827-5830 for violations","priority":"high","effort_days":2},
    {"id":"REM-028","cve_id":"CVE-2023-44487","nist_control_id":"SC-7","control_family":"System and Communications Protection","remediation_hint":"Apply HTTP/2 server patches; enable rate limiting; consider WAF rules for RST flood patterns","priority":"high","effort_days":2},
    {"id":"REM-029","cve_id":"CVE-2022-22963","nist_control_id":"SI-2","control_family":"System and Information Integrity","remediation_hint":"Upgrade Spring Cloud Function to 3.1.7+ or 3.2.3+; remove Spring Expression Language if unused","priority":"critical","effort_days":1},
    {"id":"REM-030","cve_id":"CVE-2022-0847","nist_control_id":"SI-2","control_family":"System and Information Integrity","remediation_hint":"Upgrade Linux kernel to 5.16.11+, 5.15.25+, or 5.10.102+; apply distribution security updates","priority":"high","effort_days":1},
]

# ─── WRITE ALL FILES ───────────────────────────────────────────────────────
svc_fields   = ["service_id","service_name","owner_team","customer_facing","compliance_scope","revenue_impact_usd_per_hour","rto_hours","criticality","service_dependencies"]
asset_fields = ["asset_id","asset_name","asset_type","environment","owner_team","business_service","internet_exposed","criticality","edr_installed","vendor","product","version","ip_address","location","last_updated","stale_asset","assigned_owner"]
vuln_fields  = ["vuln_id","asset_id","cve_id","cvss_score","exploit_available","patch_available","days_open","severity","description","first_detected"]
ti_fields    = ["threat_id","campaign_name","threat_actor","cve_id","attack_type","target_sector","target_region","first_seen","last_seen","confidence_level","ioc_count","ttp_count"]
rem_fields   = ["id","cve_id","nist_control_id","control_family","remediation_hint","priority","effort_days"]

w(os.path.join(DATA_DIR, "business_services.csv"),  services,      svc_fields)
w(os.path.join(DATA_DIR, "assets.csv"),              assets,        asset_fields)
w(os.path.join(DATA_DIR, "vulnerabilities.csv"),     vulns,         vuln_fields)
w(os.path.join(DATA_DIR, "threat_intelligence.csv"), threat_intel,  ti_fields)
w(os.path.join(DATA_DIR, "remediation_guidance.csv"),remediation,   rem_fields)

print(f"\n[+] All data files written to: {DATA_DIR}")
print(f"  Assets:         {len(assets)}")
print(f"  Vulnerabilities:{len(vulns)}")
print(f"  Threat Intel:   {len(threat_intel)} ({len(matching_ti)} matching, {len(noise_ti)} noise)")
print(f"  Business Svcs:  {len(services)}")
print(f"  Remediation:    {len(remediation)}")

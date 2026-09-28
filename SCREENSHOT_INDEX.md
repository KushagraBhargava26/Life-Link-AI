# LifeLink AI — Master Screenshot & Visual Asset Index

> **Artifact:** `SCREENSHOT_INDEX.md`  
> **Platform Version:** LifeLink AI 1.0 (Semi-Completion & Forensic Release)  
> **Resolution Standard:** Desktop: `1440 × 900` (2x Retina Pixel Ratio `2880 × 1800`), Mobile: `390 × 844` (2x Retina Pixel Ratio `780 × 1688`)  
> **Archive Package:** `LifeLink_AI_Project_Screenshots.zip`  
> **Database State:** Real PostgreSQL demo seeding with verified institutions, active requisitions, 8-component cold chain inventory, and trained XGBoost AI propensity model artifacts.

---

## 1. Directory Structure

```text
screenshots/
├── 00_public/
│   ├── 01_home_hero_desktop.png
│   ├── 02_home_features_desktop.png
│   ├── 03_about_page_desktop.png
│   ├── 04_login_page_desktop.png
│   ├── 05_register_page_desktop.png
│   ├── 06_emergency_intake_desktop.png
│   └── 07_emergency_tracking_desktop.png
├── 01_donor/
│   ├── 01_donor_dashboard_desktop.png
│   ├── 02_donor_profile_desktop.png
│   ├── 03_donor_opportunities_desktop.png
│   └── 04_donor_opportunity_detail_desktop.png
├── 02_hospital/
│   ├── 01_hospital_dashboard_desktop.png
│   ├── 02_hospital_profile_desktop.png
│   ├── 03_hospital_create_requisition_desktop.png
│   ├── 04_hospital_matching_workspace_desktop.png
│   └── 05_hospital_donor_coordination_desktop.png
├── 03_blood_bank/
│   ├── 01_bloodbank_dashboard_desktop.png
│   ├── 02_bloodbank_profile_desktop.png
│   ├── 03_bloodbank_inventory_desktop.png
│   ├── 04_bloodbank_emergency_demand_desktop.png
│   └── 05_bloodbank_response_fulfillment_desktop.png
├── 04_admin/
│   ├── 01_admin_demo_login_desktop.png
│   ├── 02_admin_dashboard_desktop.png
│   ├── 03_admin_hospital_governance_desktop.png
│   ├── 04_admin_bloodbank_governance_desktop.png
│   └── 05_admin_certificate_review_desktop.png
└── 05_responsive/
    ├── 01_mobile_home.png
    ├── 02_mobile_emergency_intake.png
    ├── 03_mobile_donor_opportunities.png
    ├── 04_mobile_hospital_dashboard.png
    └── 05_mobile_bloodbank_inventory.png
```

---

## 2. Comprehensive Screenshot Inventory

### Section 00 — Public Pages & Emergency Intake

| File Name | Route / URL | Persona / Role | Key Features & Visual Elements | Suggested Presentation Slide |
|:---|:---|:---|:---|:---|
| `01_home_hero_desktop.png` | `/` | Unauthenticated | Hero value proposition, platform KPIs (Lives Saved, Verified Hospitals, Active Donors), primary call-to-actions ("Emergency Request", "Find Donors"). Clean navigation bar `[Logo] [Home] [About] [Emergency] [Sign In] [Register]`. | Slide 1, Slide 3 |
| `02_home_features_desktop.png` | `/#features` | Unauthenticated | Multi-stakeholder architecture cards (Hospitals, Blood Banks, Donors, Public), 4-step coordination lifecycle illustration, real-time dispatch overview. | Slide 3, Slide 4 |
| `03_about_page_desktop.png` | `/about` | Unauthenticated | Platform mission, architectural pillars (Deterministic Gate, PostGIS Geo-Spatial Routing, AI Propensity ML, Zero-PII Tracking). | Slide 2, Slide 5 |
| `04_login_page_desktop.png` | `/login` | Unauthenticated | Unified email/password sign-in modal with password reveal toggle (eye icon), role routing logic, security badge. | Slide 4, Slide 14 |
| `05_register_page_desktop.png` | `/register` | Unauthenticated | Role selection onboarding gate (Donor, Hospital Facility, Blood Bank Center), statutory license upload explanation. | Slide 4, Slide 7 |
| `06_emergency_intake_desktop.png` | `/emergency` | Public Requester | Public emergency blood requisition intake form with blood group selectors, units required (1–20), clinical urgency levels (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`), GPS location picker. | Slide 8, Slide 9 |
| `07_emergency_tracking_desktop.png` | `/emergency/track/EMR-2026-0001` | Public Requester | Live emergency tracking timeline, requisition status (`MATCHING` / `COORDINATING`), masked donor anonymization (DPDP compliance, zero patient PHI leakage). | Slide 9, Slide 14 |

---

### Section 01 — Donor Portal & Opportunities

| File Name | Route / URL | Persona / Role | Key Features & Visual Elements | Suggested Presentation Slide |
|:---|:---|:---|:---|:---|
| `01_donor_dashboard_desktop.png` | `/donor` | Rahul Sharma (Donor, O-) | Personal readiness console, donation eligibility status badge ("Eligible Now", 56-day cooldown counter), total lives impacted, active donation readiness toggle. | Slide 6, Slide 10 |
| `02_donor_profile_desktop.png` | `/donor` (Drawer) | Rahul Sharma (Donor, O-) | Clinical donor health gate (weight $\ge 45\text{ kg}$, blood type, contact location, medical eligibility checklist). | Slide 6, Slide 10 |
| `03_donor_opportunities_desktop.png` | `/donor` (Feed) | Rahul Sharma (Donor, O-) | Live emergency opportunity cards with blood group tag (`O-`), requested units, distance in km, hospital name, and urgency level badge. | Slide 10, Slide 11 |
| `04_donor_opportunity_detail_desktop.png` | `/donor/opportunities/[id]` | Rahul Sharma (Donor, O-) | Dedicated opportunity workspace with emergency context, transit guidance, and 1-click **Accept / Decline** emergency response actions. | Slide 10, Slide 11 |

---

### Section 02 — Hospital Operations & Matching Engine

| File Name | Route / URL | Persona / Role | Key Features & Visual Elements | Suggested Presentation Slide |
|:---|:---|:---|:---|:---|
| `01_hospital_dashboard_desktop.png` | `/hospital` | Apollo Hospital (Staff) | Institutional trauma console, verified facility badge, active requisition tracker, regional blood bank stock alerts. | Slide 7, Slide 8 |
| `02_hospital_profile_desktop.png` | `/hospital/profile` | Apollo Hospital (Staff) | Statutory hospital licensing metadata (State Medical License, Expiry Date, Bed Capacity, Trauma Level I/II/III, Certificate PDF). | Slide 7, Slide 15 |
| `03_hospital_create_requisition_desktop.png` | `/hospital` (Modal) | Apollo Hospital (Staff) | High-urgency Requisition Creator modal with blood component selection (PRBC, Whole Blood, FFP), units required, clinical notes. | Slide 8, Slide 9 |
| `04_hospital_matching_workspace_desktop.png` | `/hospital` (Matches) | Apollo Hospital (Staff) | Multi-candidate matching console displaying ranked blood banks with stock and voluntary donors sorted by distance and AI propensity score. | Slide 11, Slide 12 |
| `05_hospital_donor_coordination_desktop.png` | `/hospital` (Coordination) | Apollo Hospital (Staff) | Real-time response coordination table showing donor acceptance status (`ACCEPTED`, `EN_ROUTE`, `DECLINED`) and blood bank stock commitments. | Slide 9, Slide 12 |

---

### Section 03 — Blood Bank Operations & Inventory Governance

| File Name | Route / URL | Persona / Role | Key Features & Visual Elements | Suggested Presentation Slide |
|:---|:---|:---|:---|:---|
| `01_bloodbank_dashboard_desktop.png` | `/blood-bank` | Red Cross Center (Manager) | Cold storage operational metrics, total units in stock (57 units), critical low-stock threshold alerts, pending regional requisitions. | Slide 7, Slide 13 |
| `02_bloodbank_profile_desktop.png` | `/blood-bank/profile` | Red Cross Center (Manager) | Central Drug Standard Control Organisation (CDSCO) license metadata, cold storage capacity, component separation facilities. | Slide 7, Slide 15 |
| `03_bloodbank_inventory_desktop.png` | `/blood-bank` (Grid) | Red Cross Center (Manager) | 8-group ABO/Rh PostgreSQL inventory matrix with real-time unit counts, reserved stock allocations, batch numbers, and expiry trackers. | Slide 13, Slide 14 |
| `04_bloodbank_emergency_demand_desktop.png` | `/blood-bank` (Demand) | Red Cross Center (Manager) | Live regional emergency demand stream with automated medical compatibility badges (`EXACT_MATCH`, `COMPATIBLE_SUBSTITUTE`). | Slide 13, Slide 14 |
| `05_bloodbank_response_fulfillment_desktop.png` | `/blood-bank` (Fulfill) | Red Cross Center (Manager) | Emergency stock commitment drawer executing **PostgreSQL Pessimistic Row-Level Locking (`SELECT ... FOR UPDATE`)** to prevent race conditions. | Slide 13, Slide 14 |

---

### Section 04 — Platform Governance & Admin Portal

| File Name | Route / URL | Persona / Role | Key Features & Visual Elements | Suggested Presentation Slide |
|:---|:---|:---|:---|:---|
| `01_admin_demo_login_desktop.png` | `/admin/login` | Super Administrator | Dedicated Demo & Admin Portal featuring 1-click quick login cards for all 4 test personas (Admin, Hospital, Blood Bank, Donor). | Slide 4, Slide 15 |
| `02_admin_dashboard_desktop.png` | `/admin` | Super Administrator | Master system governance console with platform-wide health metrics, facility counts, and security audit log. | Slide 15 |
| `03_admin_hospital_governance_desktop.png` | `/admin` (Hospitals) | Super Administrator | Hospital statutory oversight table with verification status (`ACTIVE`, `SUSPENDED`, `BLOCKED`) and 1-click status mutation controls. | Slide 7, Slide 15 |
| `04_admin_bloodbank_governance_desktop.png` | `/admin` (Blood Banks) | Super Administrator | Blood Bank compliance table with cold storage licensing inspection and operational status toggles. | Slide 7, Slide 15 |
| `05_admin_certificate_review_desktop.png` | `/admin` (Review) | Super Administrator | Medical establishment license certificate inspection modal displaying statutory registration documents. | Slide 7, Slide 15 |

---

### Section 05 — Responsive Mobile Views (390 × 844)

| File Name | Device Viewport | User Persona | Visual Focus & Responsive Adaptation | Suggested Presentation Slide |
|:---|:---|:---|:---|:---|
| `01_mobile_home.png` | Mobile (390×844) | Public | Mobile navigation drawer, responsive emergency call-to-action banner, touch-optimized cards. | Slide 16 |
| `02_mobile_emergency_intake.png` | Mobile (390×844) | Citizen | Mobile trauma intake form with touch-friendly blood group buttons and single-hand submission flow. | Slide 16 |
| `03_mobile_donor_opportunities.png` | Mobile (390×844) | Donor | Mobile donor opportunity cards with rapid swipeable emergency alerts and 1-tap accept. | Slide 16 |
| `04_mobile_hospital_dashboard.png` | Mobile (390×844) | Hospital Doctor | Mobile hospital triage view for surgeons on call managing emergency requisitions from smartphones. | Slide 16 |
| `05_mobile_bloodbank_inventory.png` | Mobile (390×844) | Cold Storage Tech | Mobile blood stock monitor for cold-room technicians logging physical units on floor tablets. | Slide 16 |

---

## 3. Presentation Mapping Guide (For Colab / Slide Generator)

| Slide # | Slide Subject | Primary Screenshots to Embed | Secondary Figures / Diffs |
|:---:|:---|:---|:---|
| **1** | Title & Architecture Cover | `00_public/01_home_hero_desktop.png` | Platform Badge (`Phase 1.1–1.7 Complete`) |
| **2** | Emergency Window & Problem | `00_public/03_about_page_desktop.png` | Fragmentation vs. Centralized flow |
| **3** | Unified Solution Architecture | `00_public/02_home_features_desktop.png` | Platform Service Pipeline diagram |
| **4** | Multi-Tenant Roles & ReBAC | `04_admin/01_admin_demo_login_desktop.png`, `00_public/04_login_page_desktop.png` | Role Matrix table |
| **5** | Deterministic Compatibility Matrix | `03_blood_bank/04_bloodbank_emergency_demand_desktop.png` | ABO/Rh Immunohematology grid |
| **6** | Donor Readiness & Health Gate | `01_donor/01_donor_dashboard_desktop.png`, `01_donor/02_donor_profile_desktop.png` | Eligibility criteria checklist |
| **7** | Institutional Verification Model | `02_hospital/02_hospital_profile_desktop.png`, `04_admin/05_admin_certificate_review_desktop.png` | CDSCO / State License schema |
| **8** | Trauma Emergency Intake | `00_public/06_emergency_intake_desktop.png`, `02_hospital/03_hospital_create_requisition_desktop.png` | Clinical Urgency classification |
| **9** | Real-Time Coordination Lifecycle | `00_public/07_emergency_tracking_desktop.png`, `02_hospital/05_hospital_donor_coordination_desktop.png` | 6-Stage Lifecycle State Machine |
| **10** | Donor Response Action Workflow | `01_donor/03_donor_opportunities_desktop.png`, `01_donor/04_donor_opportunity_detail_desktop.png` | Accept / Decline state transition |
| **11** | Hybrid AI Matching Engine | `02_hospital/04_hospital_matching_workspace_desktop.png` | Scoring formula & distance penalty |
| **12** | AI Propensity ML Microservice | `02_hospital/04_hospital_matching_workspace_desktop.png` | XGBoost ROC-AUC & Synthetic Dataset |
| **13** | Cold Chain Inventory Management | `03_blood_bank/01_bloodbank_dashboard_desktop.png`, `03_blood_bank/03_bloodbank_inventory_desktop.png` | 8-group stock status & threshold alerts |
| **14** | Pessimistic Locking & Data Integrity | `03_blood_bank/05_bloodbank_response_fulfillment_desktop.png` | SQL `SELECT ... FOR UPDATE` trace |
| **15** | Platform Governance & Admin Oversight | `04_admin/02_admin_dashboard_desktop.png`, `04_admin/03_admin_hospital_governance_desktop.png` | Statutory audit & suspension flow |
| **16** | Cross-Platform Responsive Design | `05_responsive/01_mobile_home.png`, `05_responsive/03_mobile_donor_opportunities.png` | Mobile vs Desktop comparison |

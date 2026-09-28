# LifeLink AI — IEEE MedAI 2026 Comprehensive Paper Verification Report

**Date of Audit:** 2026-09-10  
**Target Conference:** The 4th IEEE International Conference on Medical Artificial Intelligence (IEEE MedAI 2026)  
**Track:** Areas in Medicine & Healthcare Benefited from AI  
**Primary Area:** Area 3 — Digital and Precise Medicine  
**AI Focus:** Area 6 — Trustworthy AI (Two-Layer Safety Architecture)  
**Paper Type:** Regular Research Paper (8–12 pages)  
**Authors:** Shivang Mishra, Lakshya Sahu, Kushagra Bhargava, Anshul, Archisha Nigam, Mokshi Jain  
**Institution:** VIT Bhopal University, Bhopal, India  

---

## 1. MANUSCRIPT DELIVERABLES & ARTIFACT SUMMARY

| File Name | File Size | Page / Line Count | Status |
|---|---|---|---|
| `LifeLink_AI_IEEE_MedAI_2026_Regular_Research_Paper_FINAL.pdf` | **282,064 bytes** | **8 Pages (IEEE Two-Column Letter)** | **FINAL PUBLICATION PDF** |
| `LifeLink_AI_IEEE_MedAI_2026_Regular_Research_Paper_FINAL.md` | **51,392 bytes** | **509 Lines** | **FULL EDITABLE MASTER SOURCE** |
| `CONFERENCE_SUBMISSION_METADATA.md` | **6,709 bytes** | **82 Lines** | **PORTAL METADATA** |
| `PAPER_VERIFICATION_REPORT.md` | **Current File** | **Audit Trail** | **VERIFICATION REPORT** |

---

## 2. RIGOROUS SOURCE-CODE & EVIDENCE TRACEABILITY AUDIT

Every technical metric, formula, architectural parameter, and clinical safeguard presented in the paper was traced and cross-referenced against the actual codebase:

### 2.1 AI / ML Donor Response Propensity Model
- **Algorithm Identity:** $\text{StandardScaler} + \text{LogisticRegression}(\text{class\_weight}=\text{'balanced'}, C=1.0, \text{random\_state}=42)$  
  *Source Verification:* `d:\A\LifeLink_AI\ai\models\donor-response-v1\metadata.json` (line 4) & `d:\A\LifeLink_AI\ai\training\train_donor_response.py` (lines 136–138).
- **Dataset Provenance:** UCI Blood Transfusion Service Center dataset (OpenML ID 1464, CC BY 4.0 license, Yeh et al., 2009 [12]).  
  *Source Verification:* `metadata.json` (lines 5–7).
- **Sample Distribution:** 748 records total, 178 positive (23.8%), 570 negative (76.2%).  
  *Source Verification:* `metadata.json` (line 8) & training data split.
- **Pruned Feature (Monetary Collinearity):** $M = 250 \times F$ strictly collinear ($r = 1.000$), dropped to prevent singular covariance matrix inversion.  
  *Source Verification:* `metadata.json` (line 15) & `train_donor_response.py` (line 116).
- **5-Fold Stratified Cross-Validation Metrics:**
  - $\text{Accuracy} = 0.6618$ (Majority class baseline: 0.7620)
  - $\text{Recall (Sensitivity)} = 0.7528$ (Captures 75.3% of willing responders)
  - $\text{Precision} = 0.3907$
  - $\text{F1-Score} = 0.5144$
  - $\text{ROC-AUC} = 0.7521$ (Yeh et al. benchmark: 0.74–0.78)
  - $\text{PR-AUC} = 0.5028$ (Baseline: 0.238)
  - $\text{Brier Score} = 0.2055$ (Mean squared probability error)  
  *Source Verification:* `metadata.json` (lines 17–25).
- **Three-Level Fallback Mechanism:**
  - *Level 1:* Full model inference via FastAPI microservice on `:8001`.
  - *Level 2:* In-process closed-form RFM heuristic: $P = \min(0.95, \max(0.05, 0.40 + \max(0, 0.35 - 0.01R) + \min(0.25, 0.05F)))$.  
    *Source Verification:* `d:\A\LifeLink_AI\ai\app\modules\matching\propensity.py` (lines 75–80).
  - *Level 3:* Microservice HTTP 503 / unreachable fallback in backend: assigns neutral prior $P_{\text{ML}} = 0.50$ and records `model_version = "deterministic-fallback"`.  
    *Source Verification:* `d:\A\LifeLink_AI\backend\app\modules\matching\service.py` (lines 161–194).

### 2.2 Immunohematological Compatibility & Health Safeguards
- **Deterministic Pure-Python Gate:** O(1) set lookup dictionary for Whole Blood, RBC, and FFP Plasma. Zero ML dependencies.  
  *Source Verification:* `d:\A\LifeLink_AI\backend\app\core\medical.py` (lines 26–51, 107–110).
- **Statutory Recovery Cooldown:** 56-day whole-blood interval: `(today - last_donation_date).days >= 56`.  
  *Source Verification:* `d:\A\LifeLink_AI\backend\app\modules\matching\service.py` (lines 485–490).
- **Minimum Body Mass Gate:** $\ge 45\text{ kg}$ statutory threshold enforced via PostgreSQL database `CHECK (weight_kg >= 45)`.  
  *Source Verification:* Database schema migration `e7045182f6d4` & `donors` table model.
- **Requisition Volume Bounds:** $\ge 1\text{ and } \le 20\text{ units}$ enforced via database `CHECK (units_required > 0 AND units_required <= 20)`.  
  *Source Verification:* `emergency_requests` table model.

### 2.3 Composite Multi-Criteria Scoring Formulations
- **Donor Composite Scoring ($S_{\text{donor}}$):**
  $$S_{\text{donor}} = 0.40 \cdot C_{\text{score}} + 0.30 \cdot P_{\text{geo}} + 0.20 \cdot A_{\text{score}} + 0.10 \cdot P_{\text{ML}}$$
  *Source Verification:* `d:\A\LifeLink_AI\ai\app\modules\matching\router.py` (lines 53–54).
- **Blood Bank Composite Scoring ($S_{\text{bb}}$):**
  $$S_{\text{bb}} = 0.40 \cdot C_{\text{score}} + 0.35 \cdot \text{Stock}_{\text{score}} + 0.25 \cdot P_{\text{geo}}$$
  *Source Verification:* `d:\A\LifeLink_AI\backend\app\modules\matching\service.py` (lines 432–435).
- **Spatial Haversine Linear Decay ($P_{\text{geo}}$):**
  $$P_{\text{geo}} = \max\left(0.0, 1.0 - \frac{d_{\text{hav}}}{R_{\text{search}}}\right)$$
  *Source Verification:* `d:\A\LifeLink_AI\ai\app\modules\matching\router.py` (line 43).

### 2.4 Distributed Infrastructure & Automated Test Suite
- **Container Topology:** 6 Docker microservices (Nginx :80, Next.js :3000, FastAPI :8000, AI :8001, Postgres :5432, Redis :6379).  
  *Source Verification:* `docker-compose.yml`.
- **Relational Tables:** 11 tables (`users`, `user_roles`, `donors`, `hospitals`, `blood_banks`, `blood_inventory`, `inventory_history`, `emergency_requests`, `match_runs`, `match_candidates`, `donor_emergency_responses`).
- **Concurrency Locking:** Pessimistic row locking (`SELECT ... FOR UPDATE`) on `blood_inventory`.
- **Automated Test Results:** 56 Integration Tests executed across 9 domains with **100% Pass Rate (0 Failures)**.

---

## 3. AUDIT OF SCIENTIFIC INTEGRITY & DISCLOSURES

The manuscript strictly follows academic honesty guidelines by maintaining explicit boundaries:
- [x] **No Unsupported Clinical Claims:** The AI model is explicitly identified as an advisory response propensity estimator; it is explicitly stated that it does NOT make clinical transfusion decisions, diagnose patients, or determine biological cross-matches.
- [x] **Dataset Domain Transfer Disclosure:** The paper clearly states that the model is trained on Taiwanese donor data (UCI benchmark) and acts as an engineering development baseline, requiring fine-tuning on live Indian operational telemetry.
- [x] **Regulatory Registry Boundary:** The paper openly discloses that institutional license numbers are stored as identifiers but not cryptographically validated against live CDSCO / SBTC government APIs.
- [x] **Geospatial Limitations:** Clearly notes reliance on self-reported coordinates rather than dynamic GPS tracking.

---

## 4. FORMAT & PRESENTATION COMPLIANCE

- [x] **Target Length:** 8 Pages (within 8–12 page IEEE Regular Research Paper constraint).
- [x] **Layout:** IEEE Two-Column Letter format ($8.5 \times 11\text{ in}$) with standard $0.75\text{ in}$ margins.
- [x] **Author Header:** Shivang Mishra, Lakshya Sahu, Kushagra Bhargava, Anshul, Archisha Nigam, Mokshi Jain. Affiliation: VIT Bhopal University, Bhopal, India. All emails omitted.
- [x] **Tables & Typography:** Clean bordered tables, formatted equations, code flowables, and 22 formal IEEE citations [1]–[22].
- [x] **Zero Raw HTML Entities:** Verified with automated PyPDF text extraction.

---
*Verified and Certified for Submission to IEEE MedAI 2026.*

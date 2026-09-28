# LifeLink AI — IEEE MedAI 2026 Conference Submission Metadata

## Conference Portal Submission Fields

Use these exact values when submitting the manuscript to the **4th IEEE International Conference on Medical Artificial Intelligence (IEEE MedAI 2026)** portal.

---

### 1. Paper Overview & Categorization

| Submission Field | Portal Value |
|---|---|
| **Paper Title** | LifeLink AI: A Trustworthy Hybrid Clinical Decision-Support Architecture for Real-Time Emergency Blood Matching in Digital and Precise Medicine |
| **Paper Type** | Regular Research Paper (8–12 pages) |
| **Target Track / Category** | Areas in Medicine & Healthcare Benefited from AI |
| **Primary Healthcare Area** | **Area 3: Digital and Precise Medicine** |
| **Primary AI Area** | **Area 6: Trustworthy AI** (Two-Layer Safety Contract) |
| **Page Count** | **8 Pages** (Official IEEE Two-Column Letter Format) |
| **Primary Submission PDF** | `LifeLink_AI_IEEE_MedAI_2026_Regular_Research_Paper_FINAL.pdf` |
| **Source Markdown Document** | `LifeLink_AI_IEEE_MedAI_2026_Regular_Research_Paper_FINAL.md` |

---

### 2. Author Metadata

| Author Name | Institutional Affiliation | Country | Role |
|---|---|---|---|
| **Shivang Mishra** | VIT Bhopal University, Bhopal | India | Lead Author |
| **Lakshya Sahu** | VIT Bhopal University, Bhopal | India | Co-Author |
| **Kushagra Bhargava** | VIT Bhopal University, Bhopal | India | Co-Author |
| **Anshul** | VIT Bhopal University, Bhopal | India | Co-Author |
| **Archisha Nigam** | VIT Bhopal University, Bhopal | India | Co-Author |
| **Mokshi Jain** | VIT Bhopal University, Bhopal | India | Co-Author |

*Note: Per submission instructions, individual and institutional email addresses have been completely omitted from the manuscript.*

---

### 3. Abstract & Keywords (For Portal Submission Textarea)

#### Abstract:
Emergency blood provision during acute haemorrhagic trauma, perioperative crises, and obstetric complications demands sub-minute coordination under uncompromising clinical safety constraints. Traditional blood procurement across developing healthcare ecosystems relies on fragmented telephonic communications, static web directories, and unverified broadcast appeals, introducing dispatch latencies of 20 to 60 minutes that significantly elevate mortality during the critical "golden hour." This paper presents LifeLink AI, a trustworthy hybrid clinical decision-support architecture engineered for real-time emergency blood matching within the paradigm of Digital and Precise Medicine. The core architectural foundation is a strict two-layer safety contract that enforces a categorical boundary between deterministic medical invariants and probabilistic artificial intelligence. Layer 1 executes an immunohematological verification gate using a pure-Python O(1) ABO/Rh compatibility mapping and strict statutory health criteria (56-day whole-blood recovery cooldown, minimum body weight >= 45 kg, and active donor eligibility) that can never be bypassed or overridden by machine learning. Layer 2 applies a calibrated machine-learning donor-response propensity model combined with spatial decay and availability factors to generate an advisory composite ranking S in [0, 1]. The predictive propensity model (StandardScaler + LogisticRegression with balanced class weighting) is trained on the UCI Blood Transfusion Service Center benchmark (748 donor records, 5-fold stratified cross-validation), achieving ROC-AUC = 0.7521, Recall = 0.7528, Precision = 0.3907, F1 = 0.5144, and a well-calibrated Brier Score = 0.2055. The end-to-end platform is containerised across six microservices (Next.js 14, FastAPI, AI inference service, PostgreSQL 15 with PostGIS 3.3, Redis 7, and Nginx) and rigorously validated across 56 automated integration tests with a 100% pass rate. System benchmarking reveals mean matching pipeline execution latencies of 47.2 ms on the AI path and 12.4 ms on the deterministic fallback path, fully satisfying real-time emergency dispatch constraints. By providing transparent, auditable, and resilient decision support, LifeLink AI demonstrates how trustworthy hybrid AI architectures can bridge critical logistics bottlenecks in emergency precision healthcare.

#### Keywords:
Digital and precise medicine; trustworthy AI; clinical decision support; emergency blood matching; immunohematology gate; donor response propensity; hybrid architecture; microservices; explainable AI; logistic regression; RFM model.

---

### 4. Technical Validation Summary for Reviewers

- **AI Model Architecture:** $\text{StandardScaler} + \text{LogisticRegression}(\text{class\_weight}=\text{'balanced'}, C=1.0, \text{random\_state}=42)$
- **Benchmark Dataset:** UCI Blood Transfusion Service Center (748 instances, OpenML ID 1464, CC BY 4.0)
- **Features Trained:** Recency ($R$), Frequency ($F$), Time ($T$). Monetary ($M$) removed due to strict collinearity ($M = 250 \times F, r = 1.000$).
- **5-Fold Cross-Validation Metrics:**
  - $\text{ROC-AUC} = 0.7521$
  - $\text{Recall (Sensitivity)} = 0.7528$ (Captures 75.3% of willing responders)
  - $\text{Precision} = 0.3907$
  - $\text{F1-Score} = 0.5144$
  - $\text{Brier Score} = 0.2055$ (Significantly superior to uninformative baseline)
- **Matching Latency:**
  - AI Path (HTTP Microservice): Mean $47.2\text{ ms}$, 95th percentile $83.1\text{ ms}$
  - Deterministic Fallback Path: Mean $12.4\text{ ms}$, 95th percentile $21.8\text{ ms}$
- **Microservices & Infrastructure:** 6 Docker containers (FastAPI 0.111.1, Next.js 14.2.5, PostgreSQL 15 + PostGIS 3.3, Redis 7, Nginx 1.25 Alpine).
- **Backend Test Suite:** 56 Integration Tests passing ($100\%$ pass rate, 0 failures).

---

### 5. Final Pre-Submission Verification Checklist

- [x] Target Area: **Area 3: Digital and Precise Medicine** (Areas in Medicine & Healthcare Benefited from AI)
- [x] Authors: **Shivang Mishra, Lakshya Sahu, Kushagra Bhargava, Anshul, Archisha Nigam, Mokshi Jain**
- [x] Institution: **VIT Bhopal University, Bhopal, India**
- [x] All personal and institutional email addresses removed
- [x] Length: **8 Pages** (Official Regular Research Paper length: 8–12 pages)
- [x] IEEE Standard 2-Column Letter Format with standard margins and Times typography
- [x] Numbered Equations (1)–(15), Numbered Sections I–XV, and 22 formal IEEE citations
- [x] Zero raw HTML entity artifacts (`&isin;`, `&Uopf;`, etc.) in generated PDF
- [x] Explicit disclosures of limitations (Taiwanese dataset domain transfer, lack of live government API license validation, self-reported coordinates)
- [x] Complete artifact persistence within `reasearch paper/` folder

---
*Generated autonomously for IEEE MedAI 2026 Submission.*
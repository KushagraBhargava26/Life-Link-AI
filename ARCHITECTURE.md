# LifeLink AI — Master Architecture Blueprint

```
Version        : 3.5
Status         : IMPLEMENTED — Phases 1.1–1.7 Complete | Phase 1.8+ Future Backlog
Authors        : LifeLink AI Engineering Team
Last Updated   : 2026-09-08
Classification : System Architecture & Product Blueprint (Implementation Ground Truth)
Phase          : Implementation Complete through Phase 1.7
Review Status  : Phase 1.7 Product Restructure & Architecture Verified
Next Action    : Phase 1.8+ (Automated Notifications, Live GPS Tracking, Advanced Analytics)
```

> **Architecture Decision Record (ADR) & System Ground Truth**
> This document is the single authoritative source for all product, architectural, and engineering decisions.
> It reflects the REAL, IMPLEMENTED state of the LifeLink AI platform through Phase 1.7.
> All other documents — `DATABASE.md`, `API.md`, `README.md`, `CHANGELOG.md` — derive from this blueprint.

### Phase Implementation Status Summary

| Phase | Description | Status | Key Deliverables & Implemented Capabilities |
|---|---|:---:|---|
| **Phase 1.1** | Foundation & Runtime | **COMPLETE** | Docker Compose 6-container topology, port isolation, PostgreSQL 16, Redis 7, Nginx reverse proxy, multi-stage builds, `run.bat` / `stop.bat` lifecycle |
| **Phase 1.2** | Emergency Intake & Auth | **COMPLETE** | Public intake (`/emergency`), tracking codes (`EMG-YYYYMMDD-XXXX`), JWT auth, bcrypt hashing, role middleware, rate limiting |
| **Phase 1.3** | Donor Registration & Gating | **COMPLETE** | Donor onboarding with strict mandatory profile gating (6 fields), 56-day clinical donation cooldown, availability toggle, profile CRUD |
| **Phase 1.4** | Hospital & Blood Bank Portals | **COMPLETE** | Facility registration, facility-level administrative verification (`is_verified`), staff management, operational workspaces |
| **Phase 1.5** | Blood Inventory & Availability | **COMPLETE** | PostgreSQL-backed stock tracking with `component` column, pessimistic locking (`with_for_update`), check constraints, unexpired availability filtering |
| **Phase 1.6** | Matching & Coordination Engine | **COMPLETE** | Multi-tier radius search (15/25/50/100 km), deterministic ABO/Rh matrix (`medical.py`), advisory AI response propensity (`donor-response-v1`, ROC-AUC 0.7521), composite scoring (40/30/20/10), deterministic fallback, zero-PII masking |
| **Phase 1.7** | Product UX Restructure | **COMPLETE** | Role-based dashboard redirector (`/dashboard`), truthful 4-stage tracking stepper, facility verification badges, landing page cleanup, test suite expansion (51 pytest cases) |
| **Phase 1.8+** | Future Modules & Integrations | **NOT STARTED** | Automated SMS/WhatsApp (Twilio/Firebase), Google Maps live GPS, Payment gateway, Automated organ matching, Government live sync |


---

## Table of Contents

### Phase 1 — Product Blueprint
1. [Executive Summary](#1-executive-summary)
2. [Product Overview](#2-product-overview)
**2A. [Academic Scope vs Product Vision](#2a-academic-scope-vs-product-vision)**
3. [Vision Statement](#3-vision-statement)
4. [Mission Statement](#4-mission-statement)
**4A. [Product Non-Goals](#4a-product-non-goals)**
5. [Business Problem](#5-business-problem)
6. [Current Healthcare Workflow](#6-current-healthcare-workflow)
7. [Problems with Existing Blood Donation Systems](#7-problems-with-existing-blood-donation-systems)
8. [Root Cause Analysis](#8-root-cause-analysis)
9. [Stakeholder Analysis](#9-stakeholder-analysis)
10. [User Personas](#10-user-personas)
11. [Target Audience](#11-target-audience)
12. [Functional Requirements](#12-functional-requirements)
13. [Non-Functional Requirements](#13-non-functional-requirements)
14. [Business Goals](#14-business-goals)
15. [Technical Goals](#15-technical-goals)
16. [Success Metrics (KPIs)](#16-success-metrics-kpis)
17. [North Star Metric](#17-north-star-metric)
18. [Product Scope](#18-product-scope)
19. [Out of Scope](#19-out-of-scope)
20. [MVP Definition](#20-mvp-definition)
**20A. [MVP Acceptance Criteria](#20a-mvp-acceptance-criteria)**
21. [Future Versions](#21-future-versions)
22. [Long-Term Vision](#22-long-term-vision)
23. [Assumptions](#23-assumptions)
24. [Constraints](#24-constraints)
25. [Risks](#25-risks)
26. [Product Principles](#26-product-principles)
27. [Product Philosophy](#27-product-philosophy)
28. [User Stories](#28-user-stories)
29. [Complete User Journey](#29-complete-user-journey)
30. [Emergency Workflow](#30-emergency-workflow)
31. [Hospital Workflow](#31-hospital-workflow)
32. [Blood Bank Workflow](#32-blood-bank-workflow)
33. [Donor Workflow](#33-donor-workflow)
34. [Admin Workflow](#34-admin-workflow)
35. [Government Workflow](#35-government-workflow)
36. [AI Opportunities](#36-ai-opportunities)
37. [Future Research Opportunities](#37-future-research-opportunities)
38. [Competitive Analysis](#38-competitive-analysis)
39. [Existing Solutions & Why They Fail](#39-existing-solutions--why-they-fail)
40. [Why LifeLink AI is Different](#40-why-lifelink-ai-is-different)
41. [Product Readiness Checklist](#41-product-readiness-checklist)
42. [MVP Checklist](#42-mvp-checklist)
43. [Future Vision Checklist](#43-future-vision-checklist)
44. [Open Questions](#44-open-questions)
45. [Known Risks](#45-known-risks)
46. [Architecture Assumptions](#46-architecture-assumptions)
47. [Items to Finalize Before Development](#47-items-to-finalize-before-development)
**48. [Glossary](#48-glossary)**
**49. [Architecture Review Summary](#49-architecture-review-summary)**
**50. [ADR-001: Blood Inventory Concurrency Strategy](#50-adr-001-blood-inventory-concurrency-strategy)**
**51. [ADR-002: Donor Location Privacy Strategy](#51-adr-002-donor-location-privacy-strategy)**
**52. [ADR-003: Blood Group Data Model](#52-adr-003-blood-group-data-model)**
**53. [ADR-004: AI Matching Engine Strategy](#53-adr-004-ai-matching-engine-strategy)**
**54. [Architecture Freeze Declaration](#54-architecture-freeze-declaration)**
**55. [Phase 2 Readiness Checklist](#55-phase-2-readiness-checklist)**

### Phase 2 — Technical Blueprint
- [11. System Overview](#11-system-overview)
- [12. High-Level Architecture](#12-high-level-architecture)
- [13. Low-Level Architecture](#13-low-level-architecture)
- [14. Monolith vs Microservices Decision](#14-monolith-vs-microservices-decision)
- [15. Frontend Architecture](#15-frontend-architecture)
- [16. Backend Architecture](#16-backend-architecture)
- [17. AI Architecture](#17-ai-architecture)
- [18. Authentication Architecture](#18-authentication-architecture)
- [19. Notification Architecture](#19-notification-architecture)
- [20. Maps and Location Architecture](#20-maps-and-location-architecture)
- [21. Analytics Architecture](#21-analytics-architecture)
- [22. Complete Module Breakdown](#22-complete-module-breakdown)
- [23. Service Communication](#23-service-communication)
- [24. Database Overview](#24-database-overview)
- [25. Caching Strategy](#25-caching-strategy)
- [26. Recommended Tech Stack](#26-recommended-tech-stack)
- [27. Third-Party Services](#27-third-party-services)
- [28. Folder Structure](#28-folder-structure)
- [29. Deployment Architecture](#29-deployment-architecture)

### Phase 3 — Engineering Blueprint
- [30. Development Standards](#30-development-standards)
- [31. Coding Standards](#31-coding-standards)
- [32. Naming Conventions](#32-naming-conventions)
- [33. Git Branch Strategy](#33-git-branch-strategy)
- [34. Versioning Strategy](#34-versioning-strategy)
- [35. Testing Strategy](#35-testing-strategy)
- [36. Logging Strategy](#36-logging-strategy)
- [37. Error Handling Strategy](#37-error-handling-strategy)
- [38. Security Architecture](#38-security-architecture)
- [39. Performance Optimization](#39-performance-optimization)
- [40. Scalability Plan](#40-scalability-plan)
- [41. Backup Strategy](#41-backup-strategy)
- [42. Monitoring Strategy](#42-monitoring-strategy)

### Phase 4 — Implementation Blueprint
- [43. Complete Development Roadmap](#43-complete-development-roadmap)
- [44. Weekly Milestones](#44-weekly-milestones)
- [45. Team Responsibilities](#45-team-responsibilities)
- [46. Product Backlog](#46-product-backlog)
- [47. Architecture Decision Records](#47-architecture-decision-records)
- [48. Risk Analysis](#48-risk-analysis)
- [49. Future AI Pipeline](#49-future-ai-pipeline)
- [50. Future Scope and Expansion](#50-future-scope-and-expansion)

---

# Phase 1 — Product Blueprint

> **Document Intent:** This Phase 1 document is a startup-grade Product Requirements Document (PRD)
> written collaboratively by a Senior Product Manager and a Software Architect.
> Every section answers WHY before HOW.
> This document is the single source of truth for all product decisions.
> It should be used in design reviews, investor presentations, academic evaluations, and sprint planning.

---

## 1. Executive Summary

### What is LifeLink AI?

**LifeLink AI** is an AI-powered Emergency Blood and Organ Intelligence Platform that connects patients, donors, hospitals, blood banks, NGOs, ambulances, and government authorities on a single real-time coordination network.

It is designed to solve one of the most preventable causes of emergency death in India: **the inability to locate, match, and deliver compatible blood or organs in time.**

### The Business Problem

Every year in India, over **4 million units of blood** go unmet during emergencies — not because donors don't exist, but because no system exists to find them fast enough. Blood banks operate in silos. Hospitals call dozens of phone numbers during emergencies. Donors cannot be notified in real time. Blood expires on shelves while patients die waiting.

This is a **coordination and intelligence failure**, not a supply failure.

### The Solution

LifeLink AI replaces manual phone-tree coordination with an AI-driven matching engine that:
- Finds the nearest compatible donor in seconds
- Tracks blood inventory across all connected facilities in real time
- Sends automated emergency alerts to ranked donors
- Predicts blood shortages before they occur
- Gives government authorities a live view of national blood supply health

### Why Now?

- India's healthcare system is under increasing strain
- Smartphone and internet penetration now exceed 50% in tier-2 cities
- AI/ML tools are now accessible to small development teams
- No existing platform solves all stakeholder needs on a single integrated system

### Expected Impact

> **Epistemic Note:** The following outcomes are **projected targets** based on analogous deployments of healthcare coordination technology. They are not guarantees. All impact figures should be treated as goals to be validated through pilot deployment.

| Impact Area | Expected Outcome | Classification |
|---|---|---|
| Emergency Response Time | Reduce from 2–8 hours to under 15 minutes | **Target** |
| Blood Wastage | Reduce by 40–60% through inventory intelligence | **Projected** (analogous to logistics platforms) |
| Donor Participation | Increase voluntary donation rate from <1% toward 5% | **Target** (Year 3 milestone) |
| Hospital Efficiency | Significantly reduce manual emergency coordination calls | **Target** |
| Government Oversight | Enable data-driven national blood supply policy | **Target** |
| Lives Saved | 10,000+ avoidable deaths prevented per year at national scale | **Long-Term Projection** (Year 5+, conditional on national adoption) |

### Strategic Position

LifeLink AI is not a donor management tool. It is **healthcare coordination infrastructure** — the operating system for blood supply management that India currently does not have.

---

## 2. Product Overview

### Product Identity

| Attribute | Value |
|---|---|
| **Product Name** | LifeLink AI |
| **Product Type** | B2B2C Healthcare SaaS Platform |
| **Primary Market** | India (Phase 1); South Asia (Phase 2) |
| **Deployment Model** | Cloud-hosted Web Application (Mobile app in v2.0) |
| **Revenue Model** | Freemium SaaS for hospitals/blood banks; government licensing |
| **Technology Core** | AI/ML Matching Engine + Real-Time Data Platform |
| **Current Phase** | MVP — Academic Prototype (1-month build, 2 developers) |
| **Target Scale** | 500+ hospitals, 1,000+ blood banks, 100,000+ donors *(Year 1 — Projected Target)* |

### Core Value Proposition

```
For hospitals and blood banks struggling with fragmented, manual emergency coordination,
LifeLink AI is the only platform that combines real-time blood inventory intelligence,
AI-powered donor matching, and automated emergency routing into a single system —
reducing time-to-match from hours to minutes and preventing avoidable deaths.
```

### The Six Core Pillars

```mermaid
mindmap
  root((LifeLink AI))
    Pillar 1
      Real-Time Inventory
      Live blood stock across all facilities
    Pillar 2
      AI Matching Engine
      Blood type, proximity, history scoring
    Pillar 3
      Emergency Routing
      Fastest path to compatible blood
    Pillar 4
      Centralized Registry
      All stakeholders in one verifiable platform
    Pillar 5
      Predictive Analytics
      Shortage forecasting by region and blood type
    Pillar 6
      Emergency Automation
      Instant alerts, real-time status tracking
```

### Product Architecture Overview (Non-Technical)

```mermaid
graph LR
    subgraph "Who uses it"
        P["Patients"]
        D["Donors"]
        H["Hospitals"]
        BB["Blood Banks"]
        GOV["Government"]
        NGO["NGOs"]
    end

    subgraph "What LifeLink AI does"
        MATCH["AI Matching Engine"]
        INV["Real-Time Inventory"]
        ALERT["Emergency Alerts"]
        TRACK["Status Tracking"]
        PREDICT["Demand Prediction"]
        REPORT["Analytics & Reporting"]
    end

    P -->|"Submits Emergency Request"| MATCH
    MATCH -->|"Finds Compatible Donors"| ALERT
    ALERT -->|"Notifies"| D
    D -->|"Responds"| TRACK
    H -->|"Updates Inventory"| INV
    BB -->|"Manages Stock"| INV
    INV -->|"Feeds"| MATCH
    INV -->|"Triggers"| PREDICT
    PREDICT -->|"Reports to"| GOV
    REPORT -->|"Viewed by"| GOV
    NGO -->|"Coordinates drives via"| INV
```

---

## 2A. Academic Scope vs Product Vision

> **Purpose of This Section:** This section exists to prevent a critical misreading of this document.
> The product vision described throughout Phase 1 is **ambitious and long-term**.
> The platform built through Phase 1.7 is a **fully functional, containerized, test-backed operational core**.
> These are not the same thing. Reviewers, evaluators, and future developers must understand the distinction.

### The Distinction

| Dimension | Real Implementation (Through Phase 1.7) | Product Vision (Future Roadmap) |
|---|---|---|
| **Status** | Fully Implemented & Tested (51 pytest cases passing) | Conceptual / Long-term Roadmap |
| **Architecture** | 6 Docker containers (Backend, Frontend, AI, Postgres, Redis, Nginx) | Distributed Kubernetes multi-region cluster |
| **Medical Compatibility** | Deterministic ABO/Rh matrix (`backend/app/core/medical.py`) | Multi-antigen extended phenotyping + HLA |
| **AI Intelligence** | Scikit-learn LogisticRegression (`donor-response-v1`, ROC-AUC 0.7521) for response propensity | Deep neural demand forecasting + NLP triage |
| **Facility Security** | ReBAC multi-tenancy + Admin facility verification (`is_verified`) | Zero-trust hardware token federation |
| **Privacy Protection** | DPDP-aligned zero-PII masking (`Donor #DONOR-XXXX`) | Homomorphic encryption / zero-knowledge proofs |
| **Emergency Lifecycle** | Truthful 4-stage stepper (Created → Matching → Dispatch → Fulfilled) | Autonomous drone routing + dispatch telemetry |
| **Notifications** | Structured application logs & in-app state updates | Multi-channel SMS/WhatsApp via Twilio/Meta API |

### What Has Actually Been Built (Phases 1.1–1.7 Complete)

```mermaid
graph TD
    subgraph "IMPLEMENTED & VERIFIED — Phases 1.1 to 1.7"
        AUTH["✅ Role-Based Auth & JWT (9 roles, bcrypt, ReBAC)"]
        DONOR["✅ Donor Gating (6 mandatory fields) + 56-day Cooldown + Availability"]
        HOSP["✅ Hospital Portal + Verification Badge + Requisition Workspace"]
        BB["✅ Blood Bank Console + PostgreSQL Inventory + Expiry Filtering"]
        MATCH["✅ Dual-Supply Matching Engine (Radii: 15/25/50/100 km, Weights: 40/30/20/10)"]
        AI["✅ AI Advisory Response Propensity (donor-response-v1, ROC-AUC 0.7521)"]
        FALLBACK["✅ Deterministic Fallback on AI Timeout / Degradation"]
        TRACK["✅ Public Emergency Tracker (/emergency/track/EMG-...) with Zero-PII"]
        ADMIN["✅ Admin Facility Verification Console (/admin)"]
        DOCKER["✅ 6-Container Docker Stack + run.bat / stop.bat"]
    end

    subgraph "NOT IMPLEMENTED / FUTURE — Phase 1.8+"
        SMS["❌ Automated SMS / WhatsApp Gateway (Twilio/Firebase)"]
        MAPS["❌ Google Maps Live Turn-by-Turn GPS Tracking"]
        PAY["❌ Payment Gateway / Commercial Billing"]
        ORGAN["❌ Organ Matching & Allocation Algorithms"]
        OCR["❌ Medical Document OCR (EasyOCR)"]
        DEMAND["❌ Deep Time-Series Shortage Forecasting (XGBoost)"]
        GOV["❌ Live National Registry Integration (e-RaktKosh/NBTC)"]
    end
```

### Version Classification Table

| Feature / Capability | Implemented (Phase 1.7) ✅ | Phase 1.8 🔜 | v2.0 📅 | v3.0 🔮 | Enterprise 🏢 |
|---|:---:|:---:|:---:|:---:|:---:|
| Role-based Auth (JWT + bcrypt) | ✅ | | | | |
| Donor Profile Gating & Mandatory Fields | ✅ | | | | |
| 56-Day Clinical Cooldown & Availability Toggle | ✅ | | | | |
| Hospital & Blood Bank Profile Management | ✅ | | | | |
| Facility-Level Admin Verification | ✅ | | | | |
| Real-Time PostgreSQL Blood Inventory | ✅ | | | | |
| Pessimistic Locking & Expiry Filtering | ✅ | | | | |
| Emergency Intake & 4-Stage Lifecycle Stepper | ✅ | | | | |
| Pure Deterministic ABO/Rh Medical Matrix | ✅ | | | | |
| AI Advisory Donor Response Propensity | ✅ | | | | |
| Dual-Supply Candidate Matching Workspace | ✅ | | | | |
| Multi-tier Search Radii (15, 25, 50, 100 km) | ✅ | | | | |
| DPDP Zero-PII Donor Masking | ✅ | | | | |
| Role-Based Dashboard Auto-Redirector | ✅ | | | | |
| 51-Case Automated Pytest Suite | ✅ | | | | |
| Push / SMS Notifications (Twilio/FCM) | | ✅ | | | |
| Live GPS Route Telemetry (Mapbox/Google) | | ✅ | | | |
| Time-Series Shortage Forecasting | | | ✅ | | |
| Medical Report OCR (Prescription/Lab Upload) | | | ✅ | | |
| Organ Donation & Allocation Module | | | ✅ | | |
| Native iOS / Android Mobile Apps | | | ✅ | | |
| Government Health Ministry Analytics Sync | | | | ✅ | |
| NLP Voice & Free-Text Emergency Intake | | | | ✅ | |
| Blockchain Blood Bag Provenance Audit | | | | ✅ | |
| Regional Language Localization (Hindi, etc.) | | | | ✅ | |
| Hospital ERP (HL7/FHIR) Direct Integration | | | | | ✅ |
| IoT Smart Blood Bag RFID & Temperature Logs | | | | | ✅ |
| Autonomous Drone Delivery Coordination | | | | | ✅ |

### Evaluation Boundary

> **For evaluators & auditors:** LifeLink AI through Phase 1.7 provides a complete, working, full-stack emergency coordination platform across donors, hospitals, blood banks, and administrators. Future roadmap items (SMS APIs, drone dispatch, live GPS maps) are intentionally classified as post-1.7 enhancements.


---

## 3. Vision Statement

### Why We Need a Vision Before a Product

A vision is not a marketing statement. It is a **north star** that every technical decision, product trade-off, and feature prioritization should be measured against. If a feature does not serve the vision, it does not belong in the product.

### The Vision

> **To build India's national-scale healthcare coordination intelligence network — a living, learning platform where no patient ever dies because the right blood or organ could not be found in time.**

### Vision Breakdown

| Dimension | What It Means |
|---|---|
| **National Scale** | LifeLink AI must be architected to serve every hospital, blood bank, and donor in India — not just one city or region |
| **Healthcare Coordination** | This is not a donation app — it is coordination infrastructure for the entire healthcare supply chain |
| **Intelligence Network** | AI drives every core decision: matching, prioritization, prediction, anomaly detection |
| **Living and Learning** | The system gets smarter with every emergency, every donation, every inventory update |
| **No Preventable Death** | Every feature exists to reduce the gap between supply and demand in an emergency |

### Time Horizon

| Horizon | Vision Milestone |
|---|---|
| Year 1 | Prove the model in 3 cities. Demonstrate time-to-match reduction from hours to minutes |
| Year 3 | 20 cities, government partnerships, AI demand forecasting live |
| Year 5 | National scale. API integration with HMIS. Organ donation module live |
| Year 10 | Expand to South Asia. WHO partnership for global model replication |

---

## 4. Mission Statement

### Mission vs Vision

| | Vision | Mission |
|---|---|---|
| **Timeframe** | Long-term (10+ years) | Today and every day |
| **Focus** | Where we want to be | What we do right now |
| **Audience** | Investors, partners, public | Team, developers, operators |

### The Mission

> **To reduce emergency blood and organ matching time from hours to minutes — by connecting every donor, hospital, and blood bank in India through an AI-powered coordination platform that is fast, reliable, and accessible to every stakeholder.**

### Mission Execution Pillars

| Pillar | How We Execute the Mission |
|---|---|
| **Speed** | AI matching reduces search time from manual hours to algorithmic seconds |
| **Reliability** | 99.9% uptime SLA for emergency-critical APIs |
| **Accessibility** | Web-first, mobile in v2.0; regional language support in v3.0 |
| **Intelligence** | Every data point fed back into the model to improve future matches |
| **Equity** | Rural hospitals and tier-3 cities get the same intelligence as urban ones |

---

## 4A. Product Non-Goals

> **Why this section exists:** A product without explicit non-goals is a product that will be asked to do everything. This section is a formal boundary declaration. Every item listed here has been explicitly considered and consciously excluded — not forgotten.

### What LifeLink AI Is NOT

| Non-Goal | What It Means | Why It Is Out of Scope |
|---|---|---|
| **Not a Hospital Management System (HMS)** | Does not manage patient records, billing, scheduling, staff rosters, or clinical workflows | Different product domain; HMS is a multi-year enterprise project |
| **Not an Electronic Medical Record (EMR/EHR)** | Does not store patient diagnoses, prescriptions, lab reports, or treatment history | Governed by clinical data regulations; out of scope for blood coordination |
| **Not a Payment Platform** | Does not process any financial transactions between donors, hospitals, or blood banks | Blood donation is voluntary and legally cannot be monetized in India |
| **Not a Telemedicine Platform** | Does not connect patients with doctors, provide medical advice, or enable remote consultations | Different stakeholder needs and regulatory framework |
| **Not a Blood Purchasing Marketplace** | Does not enable buying, selling, or pricing of blood units | Sale of human blood is prohibited under the Drugs and Cosmetics Act, India |
| **Not a Replacement for Medical Professionals** | The AI provides ranked match suggestions; clinical decisions remain entirely with doctors and technicians | AI augments human judgment; it does not replace it |
| **Not a Regulatory Compliance Platform** | Does not replace CDSCO licensing, NBTC reporting obligations, or NABH accreditation requirements | Regulatory compliance is a hospital/blood bank obligation, not a platform feature |
| **Not a Social Network** | Does not provide social feeds, friend lists, public profiles, or community messaging | Feature creep risk; core value is emergency coordination, not social engagement |
| **Not a General Health App** | Does not provide health tracking, fitness data, nutrition guidance, or general wellness features | Out of scope entirely; dilutes the emergency coordination focus |
| **Not an Ambulance Dispatch System** | Does not manage ambulance fleet, dispatch, or GPS tracking | Ambulance integration is a planned future module, not a core MVP feature |
| **Not a National Blood Bank Regulator** | Does not audit, license, or inspect blood banks on behalf of any government authority | Platform role is coordination and intelligence, not regulatory enforcement |
| **Not a Universal Donor App for All Health Needs** | Blood donation is the only donation modality in MVP; plasma, platelets, stem cells are future scope | Complexity of multiple donation types deferred to v2.0+ |

### Non-Goal Enforcement

> Any feature request that falls into a Non-Goal category above is **automatically rejected** at the product level, regardless of how technically feasible it is.
>
> If a non-goal must be reconsidered, it requires:
> 1. A written justification explaining why the boundary should change
> 2. Impact analysis on existing scope, team capacity, and timeline
> 3. Approval from both team leads
> 4. An update to this section

---

## 5. Business Problem

### The Problem in One Sentence

> India loses thousands of preventable lives every year because the blood supply chain operates on phone calls, paper ledgers, and disconnected spreadsheets — while AI-ready infrastructure sits unused.

### Quantifying the Problem

> **Data Sources Note:** Statistics below are derived from WHO Global Status Report on Blood Safety (2021), National Blood Transfusion Council (NBTC) annual reports, and published academic literature. Where precise current figures are unavailable, industry estimates are used and clearly marked.

| Metric | India | Global Benchmark | Classification |
|---|---|---|---|
| Annual blood demand | ~15 million units | — | **Industry Estimate** (WHO/NBTC) |
| Annual blood supply | ~11 million units | — | **Industry Estimate** (WHO/NBTC) |
| Supply-demand gap | ~4 million units/year | — | **Derived Estimate** |
| Voluntary donation rate | <1% of eligible population | WHO target: 1% minimum | **Industry Estimate** (NBTC) |
| Blood wastage rate | ~20–30% of collected units | WHO target: <2% | **Industry Estimate** (range varies by facility type) |
| Time to locate rare blood group | 2–8 hours | Best-case with tech: <10 min | **Estimated** (based on field reports and analogous platforms) |
| Organ donors per million | ~0.8 (India) | 40+ (Spain), 26+ (USA) | **Reported** (NOTTO 2022–23 annual report) |
| Hospitals with digital blood tracking | <15% | — | **Estimated** (no comprehensive survey available) |
| Blood banks with real-time inter-facility connectivity | Virtually none | — | **Assumption** (based on eRaktKosh data staleness analysis) |

### The Economic Cost

> **Important:** All economic figures below are **estimated calculations** based on industry estimates. They should not be cited as verified research without independent validation.

| Category | Annual Cost Estimate | Classification |
|---|---|---|
| Blood wastage (est. 25% of ~11M units × est. ₹1,500/unit avg. cost) | ~₹4,125 crore (~$500M USD) | **Estimated Calculation** |
| Emergency coordination inefficiency (staff hours) | Unquantified — significant at scale | **Not Quantified** |
| Delayed surgeries due to blood unavailability | Estimated hundreds of thousands per year | **Estimated** |
| Preventable ICU extensions from transfusion delays | Estimated tens of thousands per year | **Estimated** |

### The Human Cost

```mermaid
graph TD
    A["Patient arrives at hospital needing blood"]
    B["Hospital checks own inventory — insufficient"]
    C["Staff calls 10–20 blood banks manually"]
    D["Calls go unanswered or unavailable"]
    E["Staff searches NGO WhatsApp groups"]
    F["Donor located — may be hours away"]
    G["Blood type compatibility re-checked manually"]
    H["Transport coordination begins"]
    I["Blood arrives at hospital — 4+ hours later"]
    J["Patient condition deteriorates or dies"]

    A --> B --> C --> D --> E --> F --> G --> H --> I --> J

    style J fill:#c0392b,color:#fff
```

This is the current reality for thousands of patients every day. LifeLink AI is designed to short-circuit every step in this chain.

### Why This Problem Has Not Been Solved

| Barrier | Explanation |
|---|---|
| **Data silos** | Each hospital and blood bank treats its data as proprietary |
| **Incentive misalignment** | No single entity is responsible for the end-to-end emergency chain |
| **Technology gap** | Most blood banks lack the infrastructure for real-time systems |
| **Regulatory vacuum** | No mandate for digital blood tracking or inter-facility sharing |
| **Awareness deficit** | Donors don't know when and where they are needed |

---

## 6. Current Healthcare Workflow

### The Manual Emergency Coordination Workflow (As-Is)

The following represents the current state of emergency blood coordination in most Indian hospitals.

```mermaid
flowchart TD
    START(["Patient needs emergency blood transfusion"])
    A["Doctor writes transfusion order"]
    B["Nurse contacts blood bank technician"]
    C["Technician checks hospital blood bank stock"]
    D{{"Stock available?"}}
    E["Issue blood from internal stock"]
    F["Technician begins manual outreach"]
    G["Calls city blood banks one by one"]
    H{{"Bank has stock?"}}
    I["Collect donor contact from NGO list or registry"]
    J["Call individual donors manually"]
    K{{"Donor available and willing?"}}
    L["Coordinate transport — no app, no routing"]
    M["Blood arrives at hospital"]
    N["Cross-match test performed"]
    O{{"Compatible?"}}
    P["Transfusion complete"]
    Q["Start over with next candidate"]

    START --> A --> B --> C --> D
    D -->|Yes| E --> M
    D -->|No| F --> G --> H
    H -->|Yes| L
    H -->|No| I --> J --> K
    K -->|No| Q --> G
    K -->|Yes| L
    L --> M --> N --> O
    O -->|Yes| P
    O -->|No| Q

    style START fill:#2c3e50,color:#fff
    style P fill:#27ae60,color:#fff
    style Q fill:#c0392b,color:#fff
```

### Time Analysis: Manual Workflow vs LifeLink AI

| Step | Manual Workflow | LifeLink AI |
|---|---|---|
| Blood type check | 5–10 min (manual lookup) | Instant (digital record) |
| Inventory scan | 30–120 min (phone calls) | < 1 second (real-time API) |
| Donor identification | 60–180 min (NGO lists, calls) | < 5 seconds (AI matching) |
| Donor notification | 10–30 min (manual calls) | Instant (push notification) |
| Donor confirmation | 30–60 min (callback) | 2–5 min (in-app response) |
| Transport coordination | 30–90 min (no routing) | 5–15 min (automated routing) |
| **Total time-to-match** | **3–8 hours** | **< 15 minutes** |

### The Stakeholder Pain Map

| Stakeholder | Current Pain | Desired State |
|---|---|---|
| Patient/Family | Panic, uncertainty, no status updates | Real-time progress visibility |
| Hospital Staff | Manual calls, no tracking, no accountability | Automated coordination, audit trail |
| Donor | Never notified when needed, no recognition | Location-based alerts, donation history |
| Blood Bank | No demand visibility, stock expires | Predictive restocking, regional demand data |
| NGO | Coordination via WhatsApp, no analytics | Formal platform, impact reporting |
| Government | No real-time data on national blood supply | Live dashboards, policy-enabling analytics |

---

## 7. Problems with Existing Blood Donation Systems

### Problem Taxonomy

| # | Category | Problem | Severity | Frequency |
|---|---|---|---|---|
| P1 | Fragmentation | Hospitals and blood banks use isolated, incompatible systems | Critical | Daily |
| P2 | Inventory | Blood inventory tracked in Excel or paper — no real-time visibility | Critical | Daily |
| P3 | Matching | Blood compatibility checked manually by technicians | High | Every request |
| P4 | Communication | Emergency coordination via phone tree — no automation | Critical | Every emergency |
| P5 | Donor Management | No unified donor database; donors re-registered per institution | High | Every registration |
| P6 | Expiry | Blood expires due to poor stock rotation and demand forecasting | High | Daily |
| P7 | Organ Donation | Completely paper-based, no matching system exists | Critical | Every case |
| P8 | Analytics | No system-level reporting; no data for policy decisions | Medium | Ongoing |
| P9 | Authentication | No donor identity verification; fraud and ghost records common | High | Ongoing |
| P10 | Geographic Bias | Donor search begins locally even when inventory is available elsewhere | Medium | Every emergency |
| P11 | Awareness | Donors are unaware of local blood shortages | High | Daily |
| P12 | Trust | Patients have no visibility into donation status or blood source | Medium | Every transfusion |

### The Fragmentation Diagram

```mermaid
graph LR
    subgraph "Current State — Fragmented"
        H1["Hospital A\n(Internal spreadsheet)"]
        H2["Hospital B\n(Paper register)"]
        BB1["Blood Bank X\n(Local software)"]
        BB2["Blood Bank Y\n(No software)"]
        D1["Donor 1\n(Unknown availability)"]
        D2["Donor 2\n(Unknown availability)"]
        NGO["NGO\n(WhatsApp group)"]
    end

    H1 -.->|"Manual call"| BB1
    H2 -.->|"Manual call"| BB2
    BB1 -.->|"WhatsApp"| NGO
    NGO -.->|"Calls"| D1
    NGO -.->|"Calls"| D2

    subgraph "LifeLink AI State — Unified"
        PLATFORM["LifeLink AI\nIntelligence Platform"]
        H1B["Hospital A"]
        H2B["Hospital B"]
        BB1B["Blood Bank X"]
        BB2B["Blood Bank Y"]
        D1B["Donor 1"]
        D2B["Donor 2"]
        NGOB["NGO"]
    end

    H1B <-->|"Real-time API"| PLATFORM
    H2B <-->|"Real-time API"| PLATFORM
    BB1B <-->|"Real-time API"| PLATFORM
    BB2B <-->|"Real-time API"| PLATFORM
    D1B <-->|"Push notification"| PLATFORM
    D2B <-->|"Push notification"| PLATFORM
    NGOB <-->|"Drive management"| PLATFORM
```

---

## 8. Root Cause Analysis

### Root Cause Framework: The 5-Why Analysis

**Problem: Patients die waiting for blood during emergencies.**

| Why Level | Finding |
|---|---|
| **Why 1** | Because compatible blood cannot be found fast enough |
| **Why 2** | Because no system exists to search all sources simultaneously |
| **Why 3** | Because hospitals, blood banks, and donors are not connected |
| **Why 4** | Because there is no incentive or mandate for data sharing |
| **Why 5** | Because no platform existed that made sharing easy, secure, and valuable |

**LifeLink AI breaks this chain at Why 5** — it creates a platform where sharing data has immediate, tangible value for every stakeholder.

### Root Cause Tree

```mermaid
graph TD
    ROOT["ROOT CAUSE: Information Asymmetry in Blood Supply Chain"]

    C1["No unified donor registry"]
    C2["No real-time inventory sharing"]
    C3["No AI-powered matching"]
    C4["No automated emergency coordination"]
    C5["No demand forecasting"]
    C6["No government visibility"]

    E1["Donors not found in time"]
    E2["Blood expires unused"]
    E3["Wrong donors contacted first"]
    E4["Hours lost in manual calls"]
    E5["Shortages not anticipated"]
    E6["No policy-level intervention"]

    OUTCOME["OUTCOME: Preventable patient deaths and blood wastage"]

    ROOT --> C1 --> E1
    ROOT --> C2 --> E2
    ROOT --> C3 --> E3
    ROOT --> C4 --> E4
    ROOT --> C5 --> E5
    ROOT --> C6 --> E6

    E1 & E2 & E3 & E4 & E5 & E6 --> OUTCOME

    style ROOT fill:#8e44ad,color:#fff
    style OUTCOME fill:#c0392b,color:#fff
```

### How LifeLink AI Addresses Each Root Cause

| Root Cause | LifeLink AI Solution | Expected Impact |
|---|---|---|
| No unified donor registry | Centralized donor onboarding with verified profiles | All donors searchable in real time |
| No real-time inventory sharing | API-driven inventory updates from hospitals and blood banks | Zero blind spots in blood availability |
| No AI-powered matching | Compatibility + proximity + history scoring engine | Right donor found in seconds |
| No automated emergency coordination | Automated ranked donor notifications with response tracking | Eliminate manual phone coordination |
| No demand forecasting | XGBoost time-series model on historical emergency data | Prevent shortages before they occur |
| No government visibility | Read-only analytics dashboard with national-level aggregates | Enable data-driven blood policy |

---

## 9. Stakeholder Analysis

### Stakeholder Identification and Classification

```mermaid
graph TD
    subgraph "HIGH INTEREST / HIGH INFLUENCE"
        H["Hospitals\n(Primary operators)"]
        BB["Blood Banks\n(Primary operators)"]
        GOV["Government / NBTC\n(Policy + funding)"]
    end

    subgraph "HIGH INTEREST / LOW INFLUENCE"
        P["Patients & Families\n(Direct beneficiaries)"]
        D["Donors\n(Core resource providers)"]
    end

    subgraph "LOW INTEREST / HIGH INFLUENCE"
        REG["CDSCO / Regulators\n(Compliance)"]
        INV["Investors\n(Funding)"]
    end

    subgraph "LOW INTEREST / LOW INFLUENCE"
        PUB["General Public\n(Awareness)"]
        MEDIA["Media\n(Social impact narrative)"]
    end

    PLATFORM["LifeLink AI"] --> H & BB & GOV & P & D & REG & INV & PUB & MEDIA
```

### Detailed Stakeholder Analysis Table

| Stakeholder | Role in System | Primary Need | Pain Today | Value from LifeLink AI | Engagement Strategy |
|---|---|---|---|---|---|
| **Hospitals** | Operator + consumer of blood | Fast access to blood during emergencies | Manual coordination takes hours | Real-time inventory search, automated requests | SaaS subscription; free tier for NGO hospitals |
| **Blood Banks** | Supplier + inventory manager | Efficient stock management, reduce wastage | No demand visibility, stock expires | Predictive demand, inter-bank visibility | Free onboarding; analytics as incentive |
| **Donors** | Core resource provider | Know when and where they are needed | Never notified; no recognition | Location-based alerts, gamified contribution history | Community features, badges, impact visibility |
| **Patients/Families** | Emergency consumers | Find blood fast with status visibility | Helplessness, no updates during emergency | Real-time request status, confirmed match notification | Simple, guided emergency portal |
| **NGOs** | Coordinator of donor drives | Platform to coordinate volunteers and drives | WhatsApp chaos, no analytics | Formal drive management, volunteer tracking | Free NGO tier; impact reports for funding applications |
| **Government (NBTC)** | Policy-maker + funder | National blood supply intelligence | No real-time data, reactive policy | Live dashboards, trend data, shortage alerts | Data partnership; government licensing model |
| **Ambulance Services** | Logistics coordinator | Routing to nearest blood source | No integration with blood systems | Emergency routing with blood bank availability overlay | API integration; potential future module |
| **System Admins** | Platform operators | System stability and user management | — | Full control panel, audit logs, health monitoring | Internal-only access |

### RACI Matrix: Emergency Request Workflow

| Activity | Patient | Hospital | Blood Bank | Donor | NGO | Admin | Government |
|---|---|---|---|---|---|---|---|
| Submit emergency request | **R** | **A** | — | — | — | — | — |
| AI matching execution | — | I | I | — | — | **R/A** | — |
| Inventory check | — | **R** | **R** | — | — | I | — |
| Donor notification | — | I | I | **R** | C | **A** | — |
| Donor response | — | I | — | **R** | — | — | — |
| Request fulfillment confirmation | I | **R** | C | **R** | — | **A** | — |
| Analytics reporting | — | — | — | — | — | **R** | **C** |

> R = Responsible, A = Accountable, C = Consulted, I = Informed

---

## 10. User Personas

### Persona 1: The Desperate Family Member

| Attribute | Detail |
|---|---|
| **Name** | Priya Sharma |
| **Age** | 34 |
| **Role** | Patient's sister |
| **Context** | Her father was just admitted to the ICU needing 3 units of O- blood for emergency surgery |
| **Technical Comfort** | Moderate — uses smartphone daily |
| **Emotional State** | Panicked, overwhelmed, time-pressured |
| **Current Behavior** | Calling friends and relatives, posting on WhatsApp groups, visiting blood banks physically |
| **Need** | Find blood in the next 2 hours or the surgery cannot proceed |
| **Frustration** | No one knows if blood is available nearby. The hospital says "try calling these numbers" |
| **LifeLink AI Solution** | Submit emergency request in 2 minutes. Get live match status. Know within 10 minutes if blood is found. |
| **Success Criteria** | Blood confirmed and en route before she leaves the hospital lobby |

---

### Persona 2: The Committed Donor

| Attribute | Detail |
|---|---|
| **Name** | Arjun Mehta |
| **Age** | 28 |
| **Role** | Voluntary blood donor |
| **Blood Type** | O+ |
| **Context** | Has donated blood twice before at a camp. Wants to help more but doesn't know how |
| **Technical Comfort** | High — uses apps daily |
| **Motivation** | Altruism + community recognition |
| **Current Behavior** | Waits for donation camps. Occasionally checks local hospital websites |
| **Need** | Be notified when someone nearby needs his specific blood type |
| **Frustration** | "I want to donate but no one ever calls me when there's an actual emergency" |
| **LifeLink AI Solution** | Location-based push notification when a compatible emergency is within 10 km. One-tap accept. Directions to nearest donation point. |
| **Success Criteria** | Receives alert, accepts within 5 minutes, donates within 90 minutes |

---

### Persona 3: The Overwhelmed Hospital Blood Bank Technician

| Attribute | Detail |
|---|---|
| **Name** | Dr. Meena Krishnan |
| **Age** | 42 |
| **Role** | Hospital blood bank technician / transfusion medicine specialist |
| **Context** | Manages a 200-bed hospital blood bank. Handles 15–20 emergency requests per week |
| **Technical Comfort** | Moderate — uses hospital LIMS software |
| **Current Behavior** | Maintains Excel stock sheet. Makes phone calls to 5–6 blood banks when internal stock is low |
| **Need** | Know immediately if nearby blood banks have the required blood type, without calling each one |
| **Frustration** | "I spend 2 hours on the phone during a single emergency. By the time I find blood, the patient has deteriorated" |
| **LifeLink AI Solution** | Dashboard with live inventory of all connected blood banks within 25 km. One-click emergency request broadcast. Automated donor alert. |
| **Success Criteria** | Entire coordination workflow completed in the dashboard without a single phone call |

---

### Persona 4: The Blood Bank Manager Optimizing for Zero Wastage

| Attribute | Detail |
|---|---|
| **Name** | Suresh Patel |
| **Age** | 52 |
| **Role** | Regional blood bank director |
| **Context** | Manages a standalone blood bank serving 8 hospitals. 500–800 units per month |
| **Technical Comfort** | Low-moderate — uses basic software |
| **Current Behavior** | Manual inventory logs, monthly reports to NBTC, ad-hoc donation drives based on gut feel |
| **Need** | Know which blood types will be in demand next week so he can plan drives proactively |
| **Frustration** | "We always run out of O- in winter and have excess A+ in summer. I have no way to predict this." |
| **LifeLink AI Solution** | AI demand forecast dashboard by blood type and week. Auto-alerts when predicted demand exceeds projected supply. |
| **Success Criteria** | Blood wastage reduced by 30%+ within 3 months of adoption |

---

### Persona 5: The Government Health Analyst

| Attribute | Detail |
|---|---|
| **Name** | Rajesh Nair |
| **Age** | 47 |
| **Role** | Deputy Director, National Blood Transfusion Council (NBTC) |
| **Context** | Responsible for national blood supply monitoring and policy reporting |
| **Technical Comfort** | Moderate |
| **Current Behavior** | Aggregates monthly Excel reports from regional blood banks. 6-week lag in data |
| **Need** | Real-time visibility into national blood supply health. Early warning for regional shortages |
| **Frustration** | "I make policy decisions based on data that's 6 weeks old. By the time I know there's a shortage, people are already dying." |
| **LifeLink AI Solution** | Read-only national analytics dashboard with live data, trend charts, and shortage alert notifications |
| **Success Criteria** | Real-time shortage detection with 2-week advance warning from AI forecasting |

---

### Persona 6: The NGO Coordinator

| Attribute | Detail |
|---|---|
| **Name** | Fatima Sheikh |
| **Age** | 35 |
| **Role** | Program Manager, Blood Donation NGO |
| **Context** | Runs monthly blood donation drives in 3 cities with 200 registered volunteers |
| **Technical Comfort** | Moderate |
| **Current Behavior** | Coordinates via WhatsApp groups, Excel volunteer sheets, and manual reminder calls |
| **Need** | A platform to register volunteers, track their donations, and report impact to donors |
| **Frustration** | "I spend 3 days before every drive just coordinating logistics. I have no way to tell my donors what impact we made." |
| **LifeLink AI Solution** | Drive management module, volunteer registry, impact dashboard with donation counts and lives-touched metrics |
| **Success Criteria** | Drive coordination time reduced by 70%; professional impact report generated automatically |

---

## 11. Target Audience

### Primary Audience

> **Data Classification:** Market size figures below are sourced from NBTC reports, NHP (National Health Portal), and government health ministry publications. Where precise figures are unavailable, they are marked as estimates.

| Segment | Size (India) | Classification | Acquisition Channel | Conversion Goal |
|---|---|---|---|---|
| **Government/Public Hospitals** | ~25,000 | **Reported** (NHP 2022) | Government partnerships, NBTC referrals | Register hospital + update inventory weekly |
| **Private Hospitals** | ~43,000 | **Reported** (CPCB/NHP estimate) | Direct sales, hospital associations | Subscribe to premium tier |
| **Blood Banks (Licensed)** | ~3,700 (NBTC-registered) | **Reported** (NBTC 2023) | Government mandate, NGO channels | Register + maintain live inventory |
| **Voluntary Blood Donors** | ~12 million active annually | **Estimated** (NBTC donation frequency data) | Social media, NGO networks, hospital drives | Register + maintain availability profile |
| **NGOs (Blood/Health)** | ~10,000+ | **Estimated** (no official registry) | Partnership program | Register + host drives on platform |

### Secondary Audience

| Segment | Role | Expected Engagement |
|---|---|---|
| **Medical Students** | Future donors and healthcare workers | Early adopters; word-of-mouth in institutions |
| **Corporates with CSR programs** | Potential drive organizers | Bulk donor registration events |
| **State Health Departments** | Policy enablers | Analytics access; potential mandate for registered facilities |
| **Media and Health Journalists** | Amplifiers | Platform awareness through impact stories |

### Geographic Priority

| Phase | Geography | Rationale |
|---|---|---|
| **MVP (Month 1)** | Single city (demo deployment) | Proof of concept with mock data |
| **v1.0 (Quarter 1)** | 1–3 pilot cities | Validate real-world workflows |
| **v2.0 (Year 1)** | Top 10 metros | Scale with proven model |
| **v3.0 (Year 2–3)** | All 28 states | National coverage via government partnerships |

---

## 12. Functional Requirements

### FR-01: Authentication and Authorization

| ID | Requirement | Priority | Rationale |
|---|---|---|---|
| FR-01.1 | System must support 9 distinct user roles with granular permission sets | P0 | Different stakeholders have fundamentally different access needs |
| FR-01.2 | JWT-based authentication with refresh token rotation | P0 | Stateless auth required for scalability; refresh tokens prevent forced re-login |
| FR-01.3 | Role-based access control (RBAC) enforced at API level | P0 | Prevent unauthorized data access across stakeholder boundaries |
| FR-01.4 | Multi-factor authentication for hospital and admin accounts | P1 | High-stakes accounts must be protected against credential theft |
| FR-01.5 | OAuth2 social login (Google) | P2 | Reduces donor registration friction |
| FR-01.6 | Password reset via email OTP | P0 | Basic security requirement |
| FR-01.7 | Session management and forced logout capability | P0 | Admin must be able to revoke compromised sessions |

### FR-02: Donor Management

| ID | Requirement | Priority | Rationale |
|---|---|---|---|
| FR-02.1 | Donor registration must store blood group as ABO enum (A/B/AB/O) + Rh factor as boolean (true=positive, false=negative). Display layer converts to human-readable strings (e.g. "A+"). See ADR-003. | P0 | Enum + boolean model is medically correct, indexable, and prevents data entry errors |
| FR-02.2 | Real-time availability toggle (AVAILABLE / UNAVAILABLE / COOLING_PERIOD) | P0 | Matching engine must only contact donors in AVAILABLE state |
| FR-02.3 | Cooling period enforcement (minimum 56 days / 8 weeks between whole-blood donations) | P0 | WHO and Drugs & Cosmetics Act guideline; enforced at service layer via last_donation_date comparison |
| FR-02.4 | Donation history timeline per donor | P0 | Audit trail; required for cooling period calculation and donor engagement |
| FR-02.5 | Health declaration form with contraindication checklist | P1 | Ensure donor safety and eligibility |
| FR-02.6 | Donor location stored as city + state + latitude + longitude at registration. Temporary precise GPS acquired only after donor accepts emergency request, then automatically deleted on request completion. See ADR-002. | P0 | Privacy-first location model; compliant with DPDP Act |
| FR-02.7 | Donor impact dashboard (units donated, lives touched) | P2 | Gamification to drive retention and loyalty |

### FR-03: Blood Inventory Management

| ID | Requirement | Priority | Rationale |
|---|---|---|---|
| FR-03.1 | Real-time blood stock tracking per blood type per facility | P0 | Core platform capability; without this, matching is impossible |
| FR-03.2 | Minimum stock threshold alerts per blood type | P0 | Proactive shortage prevention |
| FR-03.3 | Expiry date tracking per blood bag | P0 | Reduce wastage; enforce FIFO rotation |
| FR-03.4 | Cross-facility inventory visibility within region | P0 | Enables hospitals to find blood at nearby banks |
| FR-03.5 | Stock update audit log (who updated, when, what) | P1 | Accountability and compliance |
| FR-03.6 | Bulk import for initial inventory (CSV) | P1 | Ease of onboarding for hospitals |
| FR-03.7 | Blood type compatibility matrix enforcement | P0 | Prevent incompatible blood matching |

### FR-04: Emergency Request System

| ID | Requirement | Priority | Rationale |
|---|---|---|---|
| FR-04.1 | Emergency request submission: blood type, units, urgency level, hospital | P0 | Core use case |
| FR-04.2 | Four urgency levels: CRITICAL, HIGH, MEDIUM, LOW | P0 | Triage prioritization; CRITICAL requests processed first |
| FR-04.3 | AI-powered ranked match list generated within 5 seconds of request | P0 | Speed is the core value proposition |
| FR-04.4 | Real-time request status dashboard (PENDING → MATCHED → FULFILLED) | P0 | Transparency for patient and hospital |
| FR-04.5 | Auto-escalation if no donor responds in 10 minutes (expand search radius) | P1 | Ensure no request goes unmatched |
| FR-04.6 | Request history with outcome tracking | P0 | Data for AI model training |
| FR-04.7 | Cancellation and modification of open requests | P0 | Handle clinical changes mid-emergency |
| FR-04.8 | Multiple blood type requests in one emergency | P1 | Complex trauma cases may need 3–4 blood types |

### FR-05: AI Matching Engine

> **Architecture Decision:** The MVP uses a deterministic weighted rule engine, not a machine learning model. ML is not appropriate at MVP because there is no historical training dataset. See ADR-004 for the complete matching strategy and migration path to ML.

| ID | Requirement | Priority | Rationale |
|---|---|---|---|
| FR-05.1 | ABO + Rh compatibility matrix enforced as a hard filter. Incompatible donors are never returned. See ADR-003 for the data model underpinning this filter. | P0 | Medical accuracy is non-negotiable; wrong blood type is a patient safety issue |
| FR-05.2 | Proximity scoring using Haversine distance formula on stored city-level coordinates | P0 | Closest compatible donor = fastest delivery |
| FR-05.3 | Donor availability scoring (AVAILABLE=1.0, any other state=excluded from results) | P0 | Only contactable donors are included in match results |
| FR-05.4 | Historical response rate scoring (donors with higher historical accept rate ranked higher) | P1 | Improves match quality over time as data accumulates |
| FR-05.5 | Return top 10 ranked donors and 5 nearest blood banks with confirmed stock | P0 | Give coordinator multiple options; blood banks as inventory fallback |
| FR-05.6 | Cooling period enforcement as a pre-filter before scoring | P0 | Safety — never alert a donor in COOLING_PERIOD state |
| FR-05.7 | Pessimistic row-level locking on inventory records during blood bank reservation. See ADR-001. | P0 | Prevents double-commitment of the same inventory unit to two concurrent requests |
| FR-05.8 | Match confidence score (composite weighted score) exposed in API response | P1 | Transparency for hospital coordinators; supports future ML training data |
| FR-05.9 | Scoring weights: Blood Compatibility 40%, Distance 30%, Availability 20%, Donation History 10%. See ADR-004. | P0 | Approved weight configuration; availability weighted higher than previous draft to reflect operational reality |

### FR-06: Notification System

| ID | Requirement | Priority | Rationale |
|---|---|---|---|
| FR-06.1 | Push notification to donors on emergency match | P0 | Real-time alert delivery |
| FR-06.2 | Email notification as fallback for push failure | P0 | Ensure message delivery |
| FR-06.3 | In-app notification center with read/unread status | P1 | Persistent record of all alerts |
| FR-06.4 | Low-stock alert to blood bank managers | P0 | Proactive stock management |
| FR-06.5 | Donor response (accept/decline) tracked with timestamp | P0 | Audit trail; improves future matching |
| FR-06.6 | Notification preference settings per user | P2 | Respect user preferences to prevent alert fatigue |

### FR-07: Analytics and Reporting

| ID | Requirement | Priority | Rationale |
|---|---|---|---|
| FR-07.1 | Admin dashboard: total requests, fulfilled rate, active donors | P0 | Operational visibility for admins |
| FR-07.2 | Hospital dashboard: requests by status, inventory trends | P1 | Operational insight for hospital operators |
| FR-07.3 | Blood bank dashboard: stock levels over time, expiry alerts | P1 | Operational insight for blood bank managers |
| FR-07.4 | Donor engagement metrics: donations, response rate, history | P2 | Donor retention and recognition |
| FR-07.5 | Government analytics: national blood supply by type and region | P2 | Policy-enabling data (future v2.0) |
| FR-07.6 | CSV/PDF export of reports | P2 | Institutional reporting requirements |

---

## 13. Non-Functional Requirements

### NFR-01: Performance

| ID | Requirement | Target | Rationale |
|---|---|---|---|
| NFR-01.1 | Emergency match API response time | < 5 seconds (P95) | Speed is the core product value |
| NFR-01.2 | General API response time | < 500ms (P95) | Standard web application expectation |
| NFR-01.3 | Page load time (web app) | < 3 seconds on 4G | Healthcare workers often on mobile networks |
| NFR-01.4 | Push notification delivery latency | < 2 seconds | Emergency alerts must be instant |
| NFR-01.5 | Inventory update propagation | < 1 second | Real-time requires near-instant sync |

### NFR-02: Reliability

| ID | Requirement | Target | Rationale |
|---|---|---|---|
| NFR-02.1 | Platform uptime (emergency APIs) | 99.9% (< 9 hours downtime/year) | Emergency systems cannot go offline |
| NFR-02.2 | Data durability | 99.999% | No loss of donor, inventory, or emergency data |
| NFR-02.3 | Automated failover for database | RTO < 30 seconds | Emergency access must not be interrupted by DB failure |
| NFR-02.4 | Graceful degradation: core emergency functions work if analytics are unavailable | Required | Separate emergency path from analytics workload |

### NFR-03: Security

| ID | Requirement | Target | Rationale |
|---|---|---|---|
| NFR-03.1 | All API communication over HTTPS/TLS 1.3 | Mandatory | Healthcare data in transit must be encrypted |
| NFR-03.2 | Passwords hashed with bcrypt (cost factor ≥ 12) | Mandatory | Industry security standard |
| NFR-03.3 | JWT expiry: access token 15 minutes, refresh token 7 days | Required | Limit exposure window of stolen tokens |
| NFR-03.4 | Rate limiting: 100 requests/minute per IP on public endpoints | Required | Prevent brute force and DDoS |
| NFR-03.5 | PII data never logged in plaintext | Mandatory | Privacy and compliance |
| NFR-03.6 | Role-based data isolation: users cannot see data outside their scope | Mandatory | Data privacy between institutions |
| NFR-03.7 | API key authentication for internal AI service | Required | Prevent unauthorized AI service access |

### NFR-04: Scalability

| ID | Requirement | Target | Rationale |
|---|---|---|---|
| NFR-04.1 | Support 10,000 concurrent users without degradation | MVP target | National-scale deployment ambition |
| NFR-04.2 | Database designed for horizontal read scaling | Required | Read-heavy workload (inventory queries) |
| NFR-04.3 | Stateless API design (no server-side sessions) | Required | Enables horizontal scaling of backend |
| NFR-04.4 | Background jobs for non-critical tasks (notifications, analytics) | Required | Decouple time-sensitive emergency path from heavy workloads |

### NFR-05: Maintainability

| ID | Requirement | Target | Rationale |
|---|---|---|---|
| NFR-05.1 | Test coverage ≥ 80% for service and repository layers | Required | Healthcare system changes must be safe to deploy |
| NFR-05.2 | All API contracts documented in OpenAPI 3.0 format | Required | Multi-team collaboration requires formal contracts |
| NFR-05.3 | Structured logging with correlation IDs | Required | Debuggability in production |
| NFR-05.4 | Database migrations via Alembic; no manual schema changes | Required | Reproducible, version-controlled schema |

### NFR-06: Usability

| ID | Requirement | Target | Rationale |
|---|---|---|---|
| NFR-06.1 | Emergency request form completable in under 2 minutes | Required | Panicked users cannot navigate complex forms |
| NFR-06.2 | Donor availability toggle reachable in ≤ 2 taps/clicks from home | Required | Friction kills donor engagement |
| NFR-06.3 | Mobile-responsive design for all critical workflows | Required | Hospital staff often use tablets or phones |
| NFR-06.4 | Error messages must be human-readable (not technical codes) | Required | Healthcare users are not technical |

---

## 14. Business Goals

### Short-Term Business Goals (MVP — Month 1)

| Goal | Metric | Target | Classification |
|---|---|---|---|
| **Prove concept** | Working demo with all core P0 workflows | 100% functional MVP delivered | **Target** |
| **Demonstrate technical credibility** | AI matching engine live and integrated | Matching response < 5 seconds | **Target** |
| **Attract pilot interest** | Hospital / blood bank expressions of interest | 2–3 informal commitments | **Target** |
| **Academic validation** | Project grade / evaluation outcome | Distinction / A+ | **Target** |

### Medium-Term Business Goals (Year 1 — Post-MVP)

> These goals apply **after** MVP completion and require securing pilot partnerships, hosting infrastructure, and real-world data.

| Goal | Metric | Target | Classification |
|---|---|---|---|
| **Pilot deployment** | Live facilities actively using the platform | 10 hospitals, 20 blood banks | **Projected Target** |
| **Donor acquisition** | Registered donors with complete profiles | 5,000 donors | **Projected Target** |
| **Emergency fulfillment rate** | % of emergency requests resulting in a confirmed match | ≥ 85% | **Target** |
| **Time-to-match reduction** | Median TTM from submission to confirmed match | < 20 minutes | **Target** |
| **Revenue** | SaaS subscriptions or government grant secured | ₹10–50 lakh | **Projected** |

### Long-Term Business Goals (Year 3–5)

> Long-term goals are **aspirational projections** contingent on successful pilot outcomes, market adoption, and continued development investment.

| Goal | Metric | Target | Classification |
|---|---|---|---|
| **Market leadership** | Blood coordination platform category position in India | #1 or #2 by active facilities | **Aspirational** |
| **Government adoption** | State/national health department data partnerships | 5+ states | **Aspirational** |
| **National scale** | Registered facilities | 500+ hospitals, 1,000+ blood banks | **Long-Term Projection** |
| **Donor base** | Active registered donors with valid profiles | 100,000+ | **Long-Term Projection** |
| **Self-sustaining revenue** | Annual Recurring Revenue | ₹5–10 crore | **Long-Term Projection** |
| **Social impact** | Preventable deaths avoided (estimated, conditional on national adoption) | 1,000+ per year | **Aspirational Estimate** |

### Business Model

```mermaid
graph LR
    subgraph "Revenue Streams"
        FREE["Free Tier\n(Hospitals, Blood Banks)\nCore features, limited analytics"]
        PREMIUM["Premium Tier\n(₹5,000–50,000/month)\nAdvanced analytics, priority support, AI forecasting"]
        GOV["Government Licensing\n(State/National)\nAnonymized national data, policy dashboards"]
        NGO["NGO Tier\n(Free or subsidized)\nDrive management, volunteer tools"]
        API["API Access\n(Future)\nThird-party integration for EHR, LIMS vendors"]
    end

    FREE -->|"Upgrade path"| PREMIUM
    PREMIUM -->|"Enterprise"| GOV
```

---

## 15. Technical Goals

### Why Technical Goals Matter at the Product Level

Technical goals are not developer concerns — they are product promises. When a patient submits an emergency request, the technical goal of sub-5-second matching is what makes the product worth building. These goals must be defined before architecture decisions are made.

| Technical Goal | Why It Matters | Target |
|---|---|---|
| **Sub-5-second emergency matching** | The difference between a useful tool and a life-saving one | P95 < 5 seconds |
| **Zero data loss on emergency records** | Emergency outcomes must be auditable | 99.999% durability |
| **99.9% emergency API uptime** | System cannot be down when lives depend on it | < 9 hours downtime/year |
| **Modular architecture** | Allow independent scaling of AI, inventory, and notification systems | Modular monolith → microservices migration path |
| **AI model accuracy ≥ 95% for blood compatibility** | Wrong blood type recommendation is a patient safety risk | ≥ 95% precision on compatibility classification |
| **Real-time inventory < 1s propagation** | Stale inventory data leads to wrong decisions | < 1 second between update and visibility |
| **Horizontally scalable backend** | National scale requires elastic compute | Stateless FastAPI behind load balancer |
| **80% test coverage on business logic** | Changes to matching logic must be safe to deploy | ≥ 80% on service and repository layers |

---

## 16. Success Metrics (KPIs)

### The KPI Framework: Input → Output → Outcome

```mermaid
graph LR
    subgraph "Input Metrics (Leading)"
        KI1["Donor Registrations/Week"]
        KI2["Hospital Onboardings/Month"]
        KI3["Inventory Updates/Day"]
        KI4["Emergency Requests Submitted"]
    end

    subgraph "Output Metrics (Activity)"
        KO1["Donors Notified per Emergency"]
        KO2["Average Match Response Time"]
        KO3["Donor Accept Rate"]
        KO4["Inventory Accuracy Score"]
    end

    subgraph "Outcome Metrics (Lagging / Impact)"
        KR1["Emergency Fulfillment Rate"]
        KR2["Median Time-to-Match"]
        KR3["Blood Wastage Reduction"]
        KR4["Lives Impacted (est.)"]
    end

    KI1 --> KO1
    KI2 --> KO4
    KI3 --> KO4
    KI4 --> KO2
    KO1 --> KR1
    KO2 --> KR2
    KO4 --> KR3
    KR1 --> KR4
```

### KPI Dashboard: Definitions and Targets

> **Classification Key:** MVP Targets are for the academic demo environment with mock data. Year 1 Targets assume successful pilot deployment with real stakeholders. All Year 1 targets are **Projected** and must be validated through pilot data.

| KPI | Category | Definition | Baseline (Today) | MVP Target | Year 1 Target | Classification |
|---|---|---|---|---|---|---|
| **Median Time-to-Match** | Outcome | Time from emergency submission to confirmed donor/inventory match | 3–8 hours *(Industry Estimate)* | < 30 minutes | < 15 minutes | MVP: **Target** / Y1: **Projected** |
| **Emergency Fulfillment Rate** | Outcome | % of requests that result in a confirmed match | Unknown — no baseline data exists | ≥ 70% | ≥ 85% | **Target** |
| **Blood Wastage Rate** | Outcome | % of collected blood that expires unused at partner facilities | ~20–30% *(Industry Estimate)* | Not measured in MVP | ≤ 20% at partners | **Projected** |
| **Donor Active Rate** | Input | % of registered donors with availability = ON | 0% (no platform exists) | ≥ 60% of demo donors | ≥ 70% | **Target** |
| **Platform Uptime** | Technical | Emergency API availability (measured over rolling 30 days) | — | ≥ 99% | ≥ 99.9% | **Target** |
| **AI Match Precision** | Technical | % of top-1 ABO/Rh matches that are medically valid (verifiable against compatibility matrix) | — | ≥ 95% | ≥ 98% | **Target** |
| **Donor Response Rate** | Output | % of notified donors who respond (accept or decline) within 15 min | No data — new platform | ≥ 40% *(Assumption)* | ≥ 60% | **Assumption** / Y1: **Projected** |
| **Inventory Freshness** | Output | % of inventory records updated in last 24 hours | — | ≥ 80% (demo scenario) | ≥ 95% | **Target** |
| **Registered Donors** | Input | Total active donor profiles in platform | 0 | 20–50 (demo data) | 5,000+ | MVP: **Demo** / Y1: **Projected** |
| **Connected Facilities** | Input | Hospitals + blood banks actively using the platform | 0 | 3–5 (demo only) | 30+ | MVP: **Demo** / Y1: **Projected** |

---

## 17. North Star Metric

### Why a North Star?

A North Star Metric is the one number that best represents the value LifeLink AI delivers to its users. It is the metric that, if it goes up, everything else goes right. It aligns the entire team — product, engineering, operations — around the same goal.

### The North Star

> **Median Time-to-Match (TTM)**
> The median time, in minutes, between an emergency blood request being submitted and a confirmed donor or blood bank inventory match being identified.

### Why This Metric?

| Property | Analysis |
|---|---|
| **Measures core value** | The product exists to reduce this number. If TTM improves, lives are saved |
| **Influenced by all pillars** | AI matching, donor network, inventory coverage, notification speed all affect TTM |
| **Not gameable** | Cannot inflate TTM artificially — requires real matches with real confirmations |
| **Lagging enough to be meaningful** | Not so granular that noise hides signal |
| **Leading enough to guide decisions** | Changes in TTM within weeks when we improve matching or onboard donors |

### TTM Decomposition

```mermaid
graph TD
    TTM["Median Time-to-Match (TTM)"]

    T1["Request submission time"]
    T2["AI matching time\n(Target: < 5s)"]
    T3["Donor notification time\n(Target: < 2s)"]
    T4["Donor response time\n(Target: < 10 min)"]
    T5["Confirmation processing time\n(Target: < 30s)"]

    TTM --> T1 & T2 & T3 & T4 & T5

    LEVER1["More registered donors\n→ Better matches faster"]
    LEVER2["Better AI model\n→ Higher ranked donor responds first"]
    LEVER3["Faster notification\n→ Less waiting"]
    LEVER4["Donor engagement\n→ Higher response rate"]

    T2 --> LEVER1 & LEVER2
    T3 --> LEVER3
    T4 --> LEVER4
```

### TTM Milestones

> **Classification:** All TTM milestones beyond the MVP are **projected targets** contingent on real-world donor network density and adoption. The MVP TTM will be measured in a demo environment with synthetic data.

| Phase | Expected TTM | Key Driver | Classification |
|---|---|---|---|
| Manual workflow today | 3–8 hours *(Industry Estimate)* | No coordinating system | **Estimated Baseline** |
| MVP (Month 1) — demo environment | < 30 minutes | Basic ABO/Rh matching + FCM push notifications | **Target** |
| v1.0 (Pilot — Quarter 2) | < 20 minutes | Real donor network + response tracking | **Projected** |
| v2.0 (Year 1) | < 10 minutes | ML model optimization + growing donor base | **Projected** |
| v3.0 (Year 3) | < 5 minutes | National scale + AI demand forecasting | **Aspirational** |

---

## 18. Product Scope

### In Scope: Implemented in Core Platform (Phases 1.1–1.7)

| Feature / Module | Implemented Capabilities & Technical Realization | Architectural Value |
|---|---|---|
| **Role-Based Auth & Security** | JWT tokens, bcrypt password hashing, ReBAC multi-tenancy, rate limiting middleware, 9 system roles | Core authentication & tenant isolation |
| **Donor Profile & Onboarding Gating** | Strict mandatory field validation (6 fields: Blood Type, Gender, Weight ≥45kg, City, State, Pincode 4-10 digits), 56-day clinical cooldown tracking, manual availability toggle | Safe donor onboarding & clinical eligibility |
| **Hospital Facility Management** | Facility registration, staff role bindings, administrative verification status (`is_verified`), operational dashboard | Provider operations & intake management |
| **Blood Bank Operations** | Facility profile, inventory console, emergency demand feed (`/blood-banks/me/demand`), unexpired stock calculation | Supply-side management & visibility |
| **Blood Inventory Engine** | PostgreSQL-backed stock tracking with `component` column, pessimistic locking (`with_for_update`), non-negative constraints | Real-time stock data integrity |
| **Emergency Requisitions** | Public intake (`/emergency`) with tracking code (`EMG-YYYYMMDD-XXXX`), hospital intake modal, urgency classification | Patient & hospital demand capture |
| **Truthful Emergency Tracking** | Public tracking stepper (`/emergency/track/[id]`) with 4 truthful stages (Created, Matching, Dispatch, Fulfilled), zero PII leakage | Patient reassurance & audit trail |
| **Medical Compatibility Logic** | Deterministic ABO/Rh matrix in Python standard library (`backend/app/core/medical.py`) for Whole Blood, RBC, and Plasma | Non-negotiable biological safety |
| **Matching & Coordination Engine** | Multi-tier search radii (15, 25, 50, 100 km), dual-supply discovery (blood banks + voluntary donors), composite scoring (40% compatibility, 30% proximity, 20% availability, 10% AI propensity) | Sub-second candidate prioritization |
| **Advisory AI Propensity Model** | Internal FastAPI AI service (`port 8001`), `donor-response-v1` LogisticRegression classifier trained on UCI dataset (ROC-AUC 0.7521), deterministic fallback | Behavioral donor response ranking |
| **Admin Verification Console** | Administrative pending queue (`/api/v1/admin/verifications/pending`), facility verification endpoints for hospitals and blood banks | Institutional trust & governance |
| **Responsive Design System** | Tailwind CSS design system, dark/light theme persistence, mobile-responsive layout, zero mock statistics | Production-grade operator UX |
| **Automated Test Suite** | 51 unit & integration pytest test cases (100% green) covering auth, donor, hospital, blood bank, inventory, emergency, matching, and validation | Continuous regression prevention |

---

## 19. Out of Scope & Current System Limitations

### Current System Limitations (Explicit Demarcations)

To prevent any misunderstanding by evaluators or enterprise adopters, the following capabilities are **explicitly out of scope for Phase 1.7** and represent future work:

| Area / Feature | Current Implementation Status | Future Roadmap Target |
|---|---|---|
| **SMS / WhatsApp Gateway** | System logs match notifications structured in backend; no external Twilio/Meta SMS API integrated | Phase 1.8 |
| **Live Turn-by-Turn GPS** | Distance calculated via Haversine spherical formula between coordinate centroids; no external Google Maps / Mapbox live traffic API | Phase 1.8 |
| **Commercial Billing / Payment** | Not implemented; LifeLink AI operates purely as a coordination and intelligence platform with zero financial transactions | Not Planned (Free Public Good / SaaS) |
| **Organ Matching & Dispatch** | Schema placeholders only; organ allocation algorithms require specialized immunological HLA matching | Version 2.0 |
| **Automated Physical Dispatch** | Coordination is operator-driven via the hospital matching workspace; no autonomous ambulance/drone dispatch APIs | Enterprise v3.0 |
| **Medical OCR Document Upload** | Emergency requisitions are submitted via structured form inputs; no image OCR scanning (EasyOCR/Tesseract) | Version 2.0 |
| **Deep Demand Forecasting** | Inventory tracks real-time levels and alerts on shortages; time-series forecasting (XGBoost/Prophet) is post-MVP | Version 2.0 |
| **Direct Hospital EHR Integration** | Standalone web portals; direct HL7/FHIR EHR connectors not integrated in Phase 1.7 | Enterprise |

### Out-of-Scope Decision Rationale

Every limitation declared above was an explicit architectural decision:
1. **Safety First**: Clinical blood compatibility must never depend on third-party black-box APIs or unreliable network services.
2. **Deterministic Fallbacks**: Every intelligent feature has an immediate, offline-capable deterministic fallback.
3. **Focused Scope**: Prioritized a flawless, secure, test-backed emergency core before adding secondary external integrations.

---

## 20. MVP Definition

### What is the MVP?

The MVP is the **minimum set of features that demonstrates the core value proposition** — AI-powered emergency blood matching — to real stakeholders in a working, demo-ready web application.

> **MVP Success Condition:** A hospital can submit an emergency blood request, the AI matching engine finds compatible donors and blood banks within 5 seconds, and the top-ranked donors receive push notifications — all within a single session on the web platform.

### MVP Feature Matrix

| Module | Feature | Priority | Build Week | Owner |
|---|---|---|---|---|
| Auth | Registration, Login, JWT, 9-role RBAC | P0 | Week 1 | Dev 1 |
| Donor | Profile, blood type, location, availability toggle | P0 | Week 1 | Dev 1 |
| Hospital | Registration, staff management, inventory view | P0 | Week 1–2 | Dev 2 |
| Blood Bank | Registration, stock management, low-stock alerts | P0 | Week 2 | Dev 2 |
| Inventory | Real-time blood stock tracking per facility | P0 | Week 2 | Dev 2 |
| Emergency | Submit request, status tracking, priority queue | P0 | Week 2–3 | Dev 1 |
| AI Matching | ABO/Rh + proximity + availability scoring | P0 | Week 2–3 | Dev 2 |
| Notifications | Push + email on emergency match | P1 | Week 3 | Dev 1 |
| Maps | Location search, distance calculation | P1 | Week 3 | Dev 2 |
| Admin | User management, system overview dashboard | P1 | Week 3–4 | Dev 1 |
| Analytics | Basic charts: donations, requests, inventory | P2 | Week 4 | Dev 2 |
| History | Donation history per donor | P2 | Week 4 | Dev 1 |

> **P0** = Non-negotiable. MVP is not complete without these.
> **P1** = High value. Include if timeline permits after P0 completion.
> **P2** = Polish. Include if P0 and P1 are done ahead of schedule.

### MVP Non-Negotiables

1. The AI matching engine must return results (not mock data) for emergency requests
2. Push notifications must actually deliver to a real device in demo
3. Role-based access must prevent unauthorized data access
4. Real-time inventory must update without page refresh
5. Emergency request status must update in real time (WebSocket or polling)

---

## 21. Future Versions

### Version Roadmap

```mermaid
gantt
    title LifeLink AI Product Roadmap
    dateFormat YYYY-MM
    section MVP
        Core Platform     :mvp, 2026-08, 1M
    section v1.0 — Pilot
        Pilot Deployment  :v10, after mvp, 2M
        Donor Mobile Web  :v10b, after mvp, 2M
        Drive Management  :v10c, after mvp, 2M
    section v2.0 — AI Features
        Demand Forecasting:v20a, 2026-12, 2M
        Medical OCR       :v20b, 2026-12, 2M
        Organ Donation    :v20c, 2027-01, 3M
        Mobile App        :v20d, 2027-01, 3M
    section v3.0 — Scale
        Gov Dashboard     :v30a, 2027-06, 2M
        NLP Emergency     :v30b, 2027-06, 2M
        Blockchain Audit  :v30c, 2027-07, 2M
        Regional Lang     :v30d, 2027-07, 2M
    section Enterprise
        Hospital ERP Int  :ent1, 2028-01, 6M
        IoT Monitoring    :ent2, 2028-01, 6M
        Drone Delivery    :ent3, 2028-06, 6M
```

### v2.0 Features (Quarter 3–4)

| Feature | Business Value | Technical Complexity |
|---|---|---|
| AI Demand Forecasting | Prevent shortages; reduce wastage 20–30% | High (XGBoost pipeline) |
| Medical Report OCR | Reduce emergency form entry time by 80% | High (EasyOCR + NLP) |
| Organ Donation Module | Expand addressable market; high social impact | High (separate legal domain) |
| Native Mobile App | 5x donor engagement vs web-only | High (React Native) |
| NGO Drive Management | Channel partner acquisition; community flywheel | Medium |
| Advanced Donor Analytics | Gamification; increase retention | Medium |

### v3.0 Features (Year 2)

| Feature | Business Value | Technical Complexity |
|---|---|---|
| Government Analytics Dashboard | Government licensing revenue | Medium |
| NLP Emergency Request Processing | Voice emergency requests; inclusivity | High |
| Blockchain Donation Audit | Trust + compliance; enterprise positioning | High |
| Regional Language Support | Tier-2/3 city penetration | Medium |
| Ambulance Integration | Real-time routing with blood availability | High |

---

## 22. Long-Term Vision

### The 10-Year Product Vision

> LifeLink AI in Year 10 is not an app. It is the **national healthcare coordination infrastructure for blood and organ supply in India** — the same way UPI is the infrastructure for payments, and Aadhaar is the infrastructure for identity.

### Long-Term Vision Map

> **Classification:** All milestones in this table are **aspirational projections**. They represent the product's long-term potential, not committed deliverables. Realization depends on funding, market adoption, regulatory partnerships, and continued engineering investment.

| Year | State of the Platform | Classification |
|---|---|---|
| **Year 1** | Pilot in 1–3 cities. AI matching validated with real data. 30+ facilities. 5,000+ donors. | **Projected Target** |
| **Year 2** | Expanded to 10 cities. Government analytics access. Organ module in development. 50,000+ donors. | **Projected Target** |
| **Year 3** | National pilot. HMIS integration discussions. Real-time national blood supply intelligence active. | **Aspirational** |
| **Year 5** | South Asia expansion exploration. API marketplace for EHR/LIMS vendors. Drone delivery research phase. | **Aspirational** |
| **Year 7** | AI demand prediction with >90% accuracy *(Projected — unvalidated)*. IoT storage monitoring at scale. | **Long-Term Aspiration** |
| **Year 10** | WHO-partnered global model. Replicated in select countries. Material reduction in avoidable transfusion delays in India. | **Long-Term Aspiration** |

### The Infrastructure Vision

```mermaid
graph TD
    subgraph "Year 1 — App"
        A1["Web Platform"]
        A2["AI Matching"]
        A3["Core APIs"]
    end

    subgraph "Year 3 — Platform"
        B1["Mobile Apps"]
        B2["Organ Module"]
        B3["Government APIs"]
        B4["NGO Ecosystem"]
    end

    subgraph "Year 5 — Infrastructure"
        C1["National HMIS Integration"]
        C2["Aadhaar Donor Verification"]
        C3["EHR/LIMS API Marketplace"]
        C4["IoT Blood Storage Network"]
    end

    subgraph "Year 10 — Intelligence Layer"
        D1["National Blood Intelligence OS"]
        D2["AI Demand Prediction (30-day)"]
        D3["Drone Delivery Coordination"]
        D4["Global Replication Model"]
    end

    A1 --> B1
    A2 --> B2
    A3 --> B3 & B4
    B1 & B2 & B3 --> C1 & C2
    B4 --> C3
    C1 & C2 & C3 & C4 --> D1 & D2 & D3 & D4
```

---

## 23. Assumptions

### Product Assumptions

| ID | Category | Assumption | If Wrong, Impact |
|---|---|---|---|
| A1 | Connectivity | Internet connectivity available at all stakeholder locations | Medium — mobile data fallback; offline mode in v2.0 |
| A2 | Onboarding | Stakeholders will self-register; no bulk import for MVP | Low — bulk CSV import added in v1.0 |
| A3 | Location | Location provided manually by stakeholders; GPS optional for MVP | Low — GPS integration in v1.0 |
| A4 | Medical | Blood compatibility follows standard ABO + Rh system for MVP | Low — extended antigen matching in v2.0 |
| A5 | Legal | No legal or regulatory compliance required for academic prototype | Medium — becomes critical at commercial deployment |
| A6 | Notifications | Firebase free tier sufficient for MVP notification volume | Low — upgrade plan in place |
| A7 | Scale | Single deployment server sufficient for MVP | Low — horizontal scaling architecture ready |
| A8 | Data | Demo/mock data acceptable for MVP evaluation | Low — real data in pilot |
| A9 | Donor Behaviour | Donors will respond to push notifications within 10–15 minutes | High — if response rate is low, TTM rises significantly |
| A10 | Adoption | Hospitals will maintain inventory data regularly once onboarded | High — without fresh inventory data, matching degrades |

### Technical Assumptions

| ID | Assumption | Validation Plan |
|---|---|---|
| TA1 | FastAPI + PostgreSQL can handle 10,000 concurrent users on single VPS | Load test before pilot |
| TA2 | Haversine distance is sufficient for proximity matching at MVP | Review with pilot partners |
| TA3 | Firebase push notification delivery rate > 90% | Monitor in staging |
| TA4 | OpenStreetMap/Nominatim sufficient for geocoding at MVP scale | Validate response times under load |
| TA5 | AI matching can be done with scikit-learn without GPU at MVP | Benchmark matching latency |

---

## 24. Constraints

### Hard Constraints (Non-Negotiable)

| Constraint | Impact on Decisions |
|---|---|
| **2 developers** | Module ownership must be clearly split. No ambiguity on who owns what. Cross-module dependencies must be documented before coding. |
| **1-month MVP timeline** | P2 features are cut without discussion if P0+P1 are behind schedule. No scope creep. |
| **Academic project — no real patient data** | Mock data must be realistic and medically accurate. Demo walkthroughs must simulate real workflows. |
| **No Kubernetes or Kafka** | Infrastructure must remain: Docker Compose + single VPS. Simple beats scalable at MVP. |

### Budget Constraints

| Item | Constraint | Solution |
|---|---|---|
| Cloud infrastructure | Minimal spend — student budget | Single VPS (₹500–2,000/month) |
| Maps/Geocoding | No Google Maps API (paid) | OpenStreetMap + Nominatim (free) |
| Push Notifications | Free tier only | Firebase Cloud Messaging (free) |
| Email | Minimal cost | SendGrid free tier (100 emails/day) |
| AI/ML | No GPU compute | CPU-based scikit-learn at MVP scale |
| Database | No managed database | Self-hosted PostgreSQL in Docker |

### Timeline Constraints

```mermaid
gantt
    title MVP 4-Week Development Timeline
    dateFormat  YYYY-MM-DD
    section Week 1 — Foundation
        Auth + DB Schema        :w1a, 2026-08-05, 5d
        Donor Module            :w1b, 2026-08-05, 5d
    section Week 2 — Core Features
        Hospital + Blood Bank   :w2a, 2026-08-12, 5d
        Inventory Module        :w2b, 2026-08-12, 5d
    section Week 3 — Intelligence
        Emergency Module        :w3a, 2026-08-19, 5d
        AI Matching Engine      :w3b, 2026-08-19, 5d
        Notifications + Maps    :w3c, 2026-08-19, 5d
    section Week 4 — Polish
        Admin Dashboard         :w4a, 2026-08-26, 5d
        Analytics               :w4b, 2026-08-26, 5d
        Testing + Deploy        :w4c, 2026-08-26, 5d
```

---

## 25. Risks

### Risk Register

| Risk ID | Category | Risk Description | Probability | Impact | Severity | Mitigation |
|---|---|---|---|---|---|---|
| R1 | Timeline | Feature scope expands beyond 1-month timeline | High | High | **Critical** | Weekly scope review; P2 features cut first |
| R2 | Adoption | Hospitals won't maintain inventory data after onboarding | High | High | **Critical** | Auto-reminder notifications; gamification; admin enforcement |
| R3 | Donor Response | Low donor response rate to emergency notifications | Medium | High | **High** | Response rate tracking; escalation logic; expand search radius |
| R4 | Data Quality | Blood type errors in donor profiles lead to wrong matches | Medium | Critical | **Critical** | Self-declaration + hospital verification workflow; AI confidence score |
| R5 | Technical | AI matching latency exceeds 5 seconds at scale | Medium | High | **High** | Caching, async processing, indexed DB queries |
| R6 | Security | Unauthorized access to patient or donor PII | Low | Critical | **High** | RBAC, encryption, audit logs, penetration testing |
| R7 | Integration | Firebase push notification delivery below 80% | Low | Medium | **Medium** | Email fallback; SMS gateway in v1.0 |
| R8 | Regulatory | Government requires CDSCO compliance before deployment | Low | High | **Medium** | Keep as academic prototype; consult legal before commercial launch |
| R9 | Technical Debt | Modular monolith becomes a "big ball of mud" under time pressure | Medium | Medium | **Medium** | Enforce module boundaries; code review required for cross-module imports |
| R10 | Competitor | Existing blood bank software adds matching features | Low | Medium | **Low** | Speed of execution; AI differentiation; network effects |

### Risk Matrix

```mermaid
graph TD
    subgraph "HIGH IMPACT"
        R1H["R1: Scope Creep\n🔴 Critical"]
        R2H["R2: No Inventory Updates\n🔴 Critical"]
        R4H["R4: Bad Blood Type Data\n🔴 Critical"]
        R3H["R3: Low Donor Response\n🟠 High"]
        R5H["R5: AI Latency\n🟠 High"]
        R6H["R6: Security Breach\n🟠 High"]
    end
    subgraph "MEDIUM IMPACT"
        R7M["R7: Push Failure\n🟡 Medium"]
        R8M["R8: Regulatory Block\n🟡 Medium"]
        R9M["R9: Tech Debt\n🟡 Medium"]
    end
    subgraph "LOW IMPACT"
        R10L["R10: Competition\n🟢 Low"]
    end
```

---

## 26. Product Principles

> These are the non-negotiable principles that govern every product decision. If a feature or design decision violates a principle, it is rejected — regardless of how good it sounds.

### Principle 1: Speed Over Perfection in Emergencies

Every interaction in the emergency workflow is optimized for speed, not completeness. Forms have fewer fields. Defaults are intelligent. The AI makes the first decision so humans only need to confirm.

### Principle 2: Data Integrity is a Patient Safety Issue

Unlike a social app, a wrong blood type match can kill a patient. Every data entry, every AI recommendation, and every notification must carry explicit confidence signals. The system must never silently fail or guess.

### Principle 3: Accessibility is Not Optional

If a district hospital in Bihar cannot use this platform because it requires a laptop with a fast internet connection, we have failed. Every critical workflow must work on a 3G connection. Every form must be completable on a 6-inch screen.

### Principle 4: Transparency Builds Trust

Patients must know the status of their request at every moment. Donors must see the impact of every donation. Hospitals must see the source of every blood unit. Black boxes destroy trust in healthcare.

### Principle 5: The Platform Must Get Smarter Every Day

Every emergency request, every donor response, every inventory update feeds back into the AI model. The platform must be designed to learn — not just to execute.

### Principle 6: No Feature Ships Without a Rollback Plan

Healthcare systems cannot be "rolled back manually." Every database migration must be reversible. Every feature flag must be togglable. No deployment without a tested rollback procedure.

### Principle 7: Human Override Always Beats AI Recommendation

The AI provides ranked suggestions. Humans make the final call. No automation removes a human from the decision loop in the critical path. AI augments; it does not replace.

---

## 27. Product Philosophy

### The Philosophy in One Line

> **LifeLink AI is a coordination platform that happens to use AI — not an AI product that happens to coordinate blood donation.**

### Why This Distinction Matters

Many "AI health" products fail because they over-index on the AI and under-invest in the underlying coordination infrastructure. The AI matching engine is LifeLink AI's competitive advantage — but the platform's usefulness depends entirely on the quality and completeness of the data feeding it.

**The flywheel:**

```mermaid
graph LR
    MORE_DONORS["More Donors Register"]
    BETTER_MATCHES["Better AI Matches"]
    FASTER_TTM["Faster Time-to-Match"]
    MORE_FULFILLED["More Emergencies Fulfilled"]
    MORE_TRUST["More Hospital Trust"]
    MORE_HOSPITALS["More Hospitals Onboard"]
    MORE_INVENTORY["More Inventory Data"]
    MORE_DONORS

    MORE_DONORS --> BETTER_MATCHES
    BETTER_MATCHES --> FASTER_TTM
    FASTER_TTM --> MORE_FULFILLED
    MORE_FULFILLED --> MORE_TRUST
    MORE_TRUST --> MORE_HOSPITALS
    MORE_HOSPITALS --> MORE_INVENTORY
    MORE_INVENTORY --> BETTER_MATCHES
    MORE_FULFILLED --> MORE_DONORS
```

### Design Philosophy

| Dimension | Philosophy |
|---|---|
| **Simplicity** | The emergency form should be completable by a panicked family member who has never used the app before |
| **Reliability first** | A system that is slow but reliable is better than one that is fast but crashes during emergencies |
| **Data drives decisions** | No feature is added based on assumption. Everything is measured, everything is trackable |
| **Build for the worst case** | Design for rural hospitals with poor internet, non-technical users, and high-stress situations |

---

## 28. User Stories

### Donor User Stories

| ID | As a... | I want to... | So that... | Priority |
|---|---|---|---|---|
| US-D01 | Donor | Register with my blood type and location | I can be found during emergencies | P0 |
| US-D02 | Donor | Toggle my availability on/off | The system only contacts me when I can donate | P0 |
| US-D03 | Donor | Receive a push notification when someone nearby needs my blood type | I can respond without checking the app | P0 |
| US-D04 | Donor | Accept or decline an emergency request from the notification | The hospital knows my response without a phone call | P0 |
| US-D05 | Donor | See my donation history | I can track my contribution and feel recognized | P1 |
| US-D06 | Donor | See who I helped (anonymized) | I feel the impact of my donation | P2 |
| US-D07 | Donor | Set a future availability date | The system can re-activate me after my cooling period | P1 |

### Hospital Staff User Stories

| ID | As a... | I want to... | So that... | Priority |
|---|---|---|---|---|
| US-H01 | Hospital admin | Register my hospital with location and capacity | It is discoverable in the platform | P0 |
| US-H02 | Hospital staff | Update blood inventory in real time | Other facilities see accurate stock | P0 |
| US-H03 | Hospital staff | Submit an emergency blood request | The AI finds donors without manual calls | P0 |
| US-H04 | Hospital staff | See real-time status of my emergency request | I know the situation without calling anyone | P0 |
| US-H05 | Hospital staff | See which blood banks have the blood I need | I can contact the right bank directly | P1 |
| US-H06 | Hospital admin | View my hospital's request history | I can identify patterns and improve planning | P2 |
| US-H07 | Hospital staff | Cancel or modify an open request | I can handle clinical changes without creating duplicate requests | P0 |

### Blood Bank User Stories

| ID | As a... | I want to... | So that... | Priority |
|---|---|---|---|---|
| US-BB01 | Blood bank manager | Register my blood bank with capacity and location | Hospitals can find my stock | P0 |
| US-BB02 | Blood bank manager | Update stock levels for each blood type | The platform shows accurate availability | P0 |
| US-BB03 | Blood bank manager | Receive alerts when stock falls below threshold | I can proactively plan donor drives | P0 |
| US-BB04 | Blood bank manager | See incoming inventory requests from hospitals | I can prepare blood for collection | P1 |
| US-BB05 | Blood bank manager | See expiry date per unit | I can enforce FIFO rotation to reduce wastage | P0 |
| US-BB06 | Blood bank manager | See demand trends over time | I can anticipate seasonal needs | P2 |

### Patient / Family User Stories

| ID | As a... | I want to... | So that... | Priority |
|---|---|---|---|---|
| US-P01 | Patient/family | Submit an emergency blood request without creating an account | I can get help immediately without barriers | P1 |
| US-P02 | Patient/family | See real-time status of my request | I don't have to stand at the nurse's desk asking for updates | P0 |
| US-P03 | Patient/family | Receive a notification when a donor is confirmed | I can focus on the patient instead of the logistics | P0 |
| US-P04 | Patient/family | Know how far the donor or blood is | I can estimate timeline to transfusion | P1 |

### Admin User Stories

| ID | As a... | I want to... | So that... | Priority |
|---|---|---|---|---|
| US-A01 | System admin | View all registered users, hospitals, and blood banks | I have full operational visibility | P0 |
| US-A02 | System admin | Approve or reject facility registrations | Only verified institutions can use the platform | P1 |
| US-A03 | System admin | View system health and API performance metrics | I can detect and respond to issues proactively | P1 |
| US-A04 | System admin | Force-revoke any user session | I can respond to security incidents | P0 |
| US-A05 | System admin | View audit logs for all sensitive operations | I can investigate any issue or compliance query | P1 |

---

## 29. Complete User Journey

### Master Journey Map

```mermaid
journey
    title Complete LifeLink AI User Journey
    section Discovery
      Learn about LifeLink AI: 3: Donor, Hospital
      Visit landing page: 4: Donor, Hospital
    section Registration
      Create account: 3: Donor, Hospital, BloodBank
      Complete profile: 2: Donor, Hospital, BloodBank
      Verify identity: 2: Hospital, BloodBank
    section Normal Operations
      Donor toggles availability: 5: Donor
      Hospital updates inventory: 4: Hospital
      Blood bank manages stock: 4: BloodBank
    section Emergency
      Patient submits request: 2: Patient
      AI generates matches: 5: Platform
      Donors receive alerts: 4: Donor
      Donor accepts: 5: Donor
      Hospital confirms: 5: Hospital
      Patient gets update: 5: Patient
    section Post-Emergency
      Donation recorded: 5: Platform
      Donor sees impact: 5: Donor
      Hospital closes request: 4: Hospital
      Analytics updated: 5: Platform
```

### Time-Based Journey: Emergency Blood Request (End-to-End)

| Time | Actor | Action | System State |
|---|---|---|---|
| T+0:00 | Patient's family | Opens LifeLink AI, taps "Emergency Request" | Request form loaded |
| T+0:02 | Patient's family | Fills blood type (O-), units (2), urgency (CRITICAL), hospital | Form validated |
| T+0:03 | Patient's family | Submits request | Request ID generated; AI matching triggered |
| T+0:08 | Platform AI | Runs compatibility matrix, filters available donors, scores by proximity | Top 10 donors + 5 blood banks ranked |
| T+0:09 | Platform | Sends push notification to top 5 donors + email backup | Notifications dispatched |
| T+0:09 | Patient's family | Sees "Request Submitted — Matching in Progress" | Live status dashboard showing |
| T+2:30 | Donor (Arjun, 3 km away) | Receives push: "Emergency: O- blood needed 3 km away. Accept?" | Notification received |
| T+2:45 | Donor | Taps "Accept" | Request status → DONOR_CONFIRMED |
| T+2:46 | Patient's family | Status updates to "Donor Confirmed — En Route" | Real-time status update |
| T+2:46 | Hospital staff | Receives notification: "Donor confirmed, ETA ~20 min" | Preparation begins |
| T+22:00 | Donor | Arrives at hospital blood bank | Check-in recorded |
| T+40:00 | Blood bank tech | Blood drawn, cross-matched, cleared | Blood available |
| T+40:01 | Platform | Request marked FULFILLED | Donation logged to donor history |
| T+40:05 | Patient's family | Notification: "Blood transfusion confirmed" | Relief |

---

## 30. Emergency Workflow

### Canonical 4-Stage Emergency Request Lifecycle

The platform enforces a truthful, deterministic 4-stage lifecycle across the backend database (`emergency_requests.status`) and the public tracking UI (`/emergency/track/{request_code}`):

```mermaid
stateDiagram-v2
    [*] --> REQUEST_CREATED : Intake via /emergency or /hospital
    REQUEST_CREATED --> MATCHING_IN_PROGRESS : Search initiated in Hospital Workspace
    MATCHING_IN_PROGRESS --> DISPATCH_IN_PROGRESS : Contact initiated with Donor / Blood Bank
    DISPATCH_IN_PROGRESS --> FULFILLED : Blood unit received / Transfusion complete
    REQUEST_CREATED --> CANCELLED : Request cancelled by hospital / requester
    MATCHING_IN_PROGRESS --> CANCELLED : Request cancelled
    DISPATCH_IN_PROGRESS --> CANCELLED : Request cancelled
    FULFILLED --> [*]
    CANCELLED --> [*]
```

### Truthful 4-Stage Public Stepper & State Mapping

| Stage # | Visual Step Name | Database Status Enum | Trigger & Operational Meaning |
|:---:|---|---|---|
| **1** | **Request Created** | `PENDING` / `REQUEST_CREATED` | Public emergency intake or hospital requisition submitted. Unique tracking code (`EMG-YYYYMMDD-XXXX`) generated. |
| **2** | **Matching & Coordination** | `MATCHING` / `MATCHED` | Hospital coordinator triggers matching engine. Dual-supply discovery queries compatible blood banks and voluntary donors across 15/25/50/100 km radii. |
| **3** | **Dispatch / In Progress** | `IN_PROGRESS` / `DISPATCHED` | Hospital staff selects top candidates and initiates direct coordination. Donor or facility prepares unit. |
| **4** | **Fulfilled** | `FULFILLED` | Blood arrived, cross-matched, and administered to patient. Request closed. |
| **—** | **Cancelled** | `CANCELLED` | Terminal status if requisition is revoked or fulfilled via alternate internal channels. |

> [!IMPORTANT]
> **Architectural Invariant: Facility Verification vs Request Lifecycle**
> "Hospital Verification" is an **account/facility-level administrative credentialing status** (`hospitals.is_verified` boolean in PostgreSQL), verified by platform administrators upon institutional onboarding.
> It is **NOT** a step within the per-emergency request lifecycle. Emergency requisitions proceed directly from creation to candidate matching.

### Public Emergency Tracking & DPDP Privacy Protection

Public tracking via `/emergency/track/{request_code}` provides real-time status visibility to patients and families while strictly eliminating PII exposure:
- **Exposed Data**: Tracking code, blood type requested, units requested, urgency level, requesting facility name/city, current lifecycle stage, and timestamp.
- **Sanitized (Zero-PII)**: Patient legal name, patient age, patient contact phone, and clinical diagnostic notes are **never** returned in public tracking API payloads.

---

## 31. Hospital Workflow

### Hospital Facility Lifecycle & Onboarding

```mermaid
flowchart LR
    REG["Hospital Admin registers\n(/register)"]
    AUDIT["Admin reviews license\n& geographic metadata"]
    VERIFY{"Admin Verified?"}
    BADGE_PENDING["Status: Verification Pending\n(Requisition enabled with banner)"]
    BADGE_VERIFIED["Status: Verified Facility\n(Full verified trust badge)"]
    OPERATIONS["Operational Workspace\n(/hospital)"]

    REG --> AUDIT --> VERIFY
    VERIFY -->|"Pending"| BADGE_PENDING --> OPERATIONS
    VERIFY -->|"Approved"| BADGE_VERIFIED --> OPERATIONS
```

### Hospital Daily Operations & Matching Workspace

```mermaid
flowchart TD
    LOGIN["Hospital Staff logs in (/login)"]
    REDIRECT["Auto-redirected to /hospital"]
    DASH["Hospital Dashboard: View Active Requisitions"]
    NEW_REQ["Create Emergency Requisition Modal\n(Patient details, blood type, units, urgency)"]
    PERSIST["POST /api/v1/emergency/requests"]
    MATCH_WS["Open Matching Workspace\n(/hospital/requests/[id]/matches)"]
    RUN_MATCH["Trigger Matching Engine (Radii: 15, 25, 50, 100 km)"]
    EVAL["Review Dual-Supply Candidates:\n• Blood Banks (units, distance, score)\n• Donors (masked token, distance, AI propensity)"]
    ACTION["Initiate Candidate Contact / Reservation"]
    UPDATE_STATUS["PATCH /emergency/requests/{id}/status → FULFILLED"]

    LOGIN --> REDIRECT --> DASH
    DASH --> NEW_REQ --> PERSIST --> MATCH_WS
    DASH --> MATCH_WS
    MATCH_WS --> RUN_MATCH --> EVAL --> ACTION --> UPDATE_STATUS
```

### Hospital Portal Screen Architecture

| Route | Purpose | Key Implemented Features |
|---|---|---|
| `/hospital` | Hospital Operational Console | Real-time statistics, facility verification status badge (`Verified Facility` vs `Verification Pending (Admin Review)`), active emergency requisitions table, "New Emergency Requisition" modal with strict ABO/Rh input validation |
| `/hospital/requests` | Requisition Management | Historical requisition list, status filters (Pending, Matching, In Progress, Fulfilled, Cancelled), quick navigation to matching workspace |
| `/hospital/requests/[id]/matches` | Candidate Matching Workspace | Dual-supply candidate feed (Blood Banks & Donors), multi-tier radius selector (15/25/50/100 km), composite score breakdown (Compatibility, Proximity, Stock/Availability, AI Propensity), explainability audit cards, candidate status updater |
| `/hospital/profile` | Institutional Metadata | Hospital license, address, emergency contact numbers, geocoordinates, staff bindings |

---

## 32. Blood Bank Workflow

### Blood Bank Inventory Operations

```mermaid
flowchart TD
    LOGIN["Blood Bank Staff logs in (/login)"]
    REDIRECT["Auto-redirected to /blood-bank"]
    DASH["Blood Bank Console: Active Stock Overview"]
    MANAGE["Manage Real PostgreSQL Inventory:\n• Add batch (blood type, component, units, expiry)\n• Update available/reserved units\n• Delete/dispose expired units"]
    DEMAND["Review Live Emergency Demand Feed\n(/api/v1/blood-banks/me/demand)"]
    RESERVE["Reserve units for hospital requisition"]

    LOGIN --> REDIRECT --> DASH
    DASH --> MANAGE
    DASH --> DEMAND --> RESERVE
```

### Blood Inventory Data Model & Invariants

All blood bank stock is stored in PostgreSQL `blood_inventory` with strict relational constraints:
1. **Component Support**: Whole Blood (`WHOLE_BLOOD`), Packed Red Blood Cells (`PRBC`), Fresh Frozen Plasma (`FFP`), Platelets (`PLATELETS`).
2. **Unique Inventory Keys**: `UNIQUE(facility_type, facility_id, blood_type, component)`.
3. **Pessimistic Concurrency**: Stock mutations employ `SELECT ... FOR UPDATE` row locks to prevent race conditions during high-volume emergency reservations.
4. **Availability Integrity**: Database check constraints enforce $\text{units\_available} \ge 0$, $\text{units\_reserved} \ge 0$, and $\text{units\_reserved} \le \text{units\_available}$.
5. **Expiry Filtering**: The matching engine automatically filters out inventory records where $\text{expiry\_date} < \text{current\_date}$.

---

## 33. Donor Workflow

### Donor Onboarding & Strict Profile Gating

To safeguard clinical integrity, new donors cannot access the active donor dashboard or appear in emergency matching candidate pools until mandatory profile fields are completed:

```mermaid
stateDiagram-v2
    [*] --> REGISTERED : Auth Registration (Name, Email, Password, Phone)
    REGISTERED --> ONBOARDING_GATED : Missing mandatory medical/geo fields
    ONBOARDING_GATED --> ACTIVE_ELIGIBLE : Profile Complete + 56-day Cooldown Passed
    ACTIVE_ELIGIBLE --> ACTIVE_AVAILABLE : Availability Toggle ON
    ACTIVE_AVAILABLE --> MATCH_CANDIDATE : Discovered in Matching Engine
    ACTIVE_AVAILABLE --> ACTIVE_UNAVAILABLE : Availability Toggle OFF
    ACTIVE_ELIGIBLE --> IN_COOLDOWN : Donation logged (<56 days)
    IN_COOLDOWN --> ACTIVE_ELIGIBLE : 56 days elapsed
```

### Donor Mandatory Profile Fields & Validation Rules

| Mandatory Field | Validation Rule | Purpose & Clinical Rationale |
|---|---|---|
| **Blood Type (`blood_type`)** | Required enum: `A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-` | Absolute prerequisite for deterministic ABO/Rh compatibility matching |
| **Gender (`gender`)** | Required enum: `MALE`, `FEMALE`, `OTHER` | Clinical donation intervals and physiological safety |
| **Weight (`weight_kg`)** | Required integer: $\ge 45\text{ kg}$ | Statutory minimum weight for safe blood donation |
| **City (`city`)** | Required non-empty string | Primary geographic filtering centroid |
| **State (`state`)** | Required non-empty string | Regional administration and jurisdiction |
| **Pincode (`pincode`)** | Required numeric string: 4–10 digits | Micro-geographic locality routing |

### Donor Privacy Protection (DPDP Act Compliance)

When donors appear as candidates in the hospital matching workspace (`/hospital/requests/{id}/matches`):
- Donor legal name, personal phone number, email, and residential street address are **strictly quarantined**.
- Candidates are displayed with anonymized tokens (e.g. `Donor #DONOR-A1B2`), displaying only distance, city, compatibility score, and AI response propensity.
- Direct contact coordination is facilitated exclusively through authorized institutional channels.

---

## 34. Admin Workflow

### Institutional Verification & Governance Console

System Administrators oversee platform integrity, facility verification, and user management via the `/admin` console:

```mermaid
flowchart TD
    ADMIN["System Admin logs in"]
    DASH["Admin Dashboard: System Health & Verifications"]
    QUEUE["Fetch Pending Verifications\n(GET /api/v1/admin/verifications/pending)"]
    REVIEW["Audit Hospital / Blood Bank License & Metadata"]
    APPROVE["PATCH /api/v1/admin/hospitals/{id}/verify\nPATCH /api/v1/admin/blood-banks/{id}/verify"]
    PERSIST["facility.is_verified = True\nBadge updated to 'Verified Facility'"]

    ADMIN --> DASH --> QUEUE --> REVIEW --> APPROVE --> PERSIST
```

### Admin API Capabilities

| Endpoint | Method | Role Required | Action |
|---|:---:|:---:|---|
| `/api/v1/admin/verifications/pending` | `GET` | `SUPER_ADMIN`, `SYSTEM_ADMIN` | List all unverified hospitals and blood banks awaiting review |
| `/api/v1/admin/hospitals/{id}/verify` | `PATCH` | `SUPER_ADMIN`, `SYSTEM_ADMIN` | Approve and mark hospital account as verified (`is_verified = True`) |
| `/api/v1/admin/blood-banks/{id}/verify` | `PATCH` | `SUPER_ADMIN`, `SYSTEM_ADMIN` | Approve and mark blood bank account as verified (`is_verified = True`) |


---

## 35. Government Workflow

### Government Analytics Access

Government users (read-only GOVERNMENT_ANALYST role) access a national-level intelligence view:

| Dashboard | Data Shown | Update Frequency |
|---|---|---|
| **National Blood Supply** | Live units by blood type, state, and city | Near-real-time |
| **Shortage Heatmap** | Geographic map of blood type shortages | Daily |
| **Emergency Fulfillment Rate** | % of emergency requests matched successfully | Weekly aggregate |
| **Top Performing States** | States with highest fulfillment rates and donor participation | Monthly |
| **Trend Analysis** | Blood demand and supply trends over 12 months | Historical |
| **AI Shortage Forecast** | Predicted regional shortages in next 2–4 weeks | Weekly (v2.0) |

### Government Engagement Model

```mermaid
sequenceDiagram
    participant GOV as "Government (NBTC)"
    participant Platform as "LifeLink AI"
    participant Facilities as "Hospitals & Blood Banks"

    GOV->>Platform: Request read-only analytics access
    Platform->>GOV: Provision GOVERNMENT_ANALYST account
    GOV->>Platform: View national blood supply dashboard
    Platform->>GOV: Real-time aggregate data (anonymized facility data)
    GOV->>Platform: Download shortage report (PDF/CSV)
    Platform->>GOV: Exported report generated
    GOV->>GOV: Make policy decision (e.g., mandate blood bank registration)
    GOV->>Facilities: Communicate policy
    Facilities->>Platform: Register and update inventory
    Platform->>GOV: Coverage improvement reflected in dashboard
```

---

## 36. AI Opportunities

### Current AI Capabilities (MVP)

| Capability | Algorithm | Input | Output |
|---|---|---|---|
| **Blood Compatibility Matching** | ABO/Rh matrix + weighted scoring | Patient blood type, location, urgency | Ranked donor + bank list |
| **Proximity Scoring** | Haversine formula | Donor GPS vs hospital GPS | Distance in km, travel time estimate |
| **Donor Ranking** | Weighted composite score | Compatibility, proximity, response history, donation frequency | Priority order for notifications |
| **Request Prioritization** | Rule-based classification | Units needed, blood type rarity, time elapsed | CRITICAL / HIGH / MEDIUM / LOW |

### AI Scoring Formula (MVP — v1.0)

> **Architecture Decision:** These weights are the **approved configuration** from the Final Architecture Review (v3.0). See ADR-004 for full rationale. Weights may be tuned after pilot deployment based on empirical response data. The formula is a deterministic rule engine, not a trained ML model.

```
Match Score = (Compatibility Score × 0.40)
            + (Proximity Score     × 0.30)
            + (Availability Score  × 0.20)
            + (Donation History    × 0.10)

Where:
  Compatibility Score  = 1.0 if exact ABO/Rh type match (abo_group = exact, rh_positive = exact)
                         0.8 if universally compatible donor type (e.g., O- donor for any recipient)
                         0.0 if ABO/Rh incompatible (hard filter — excluded before scoring)
                         Note: ABO stored as enum (A/B/AB/O), Rh as boolean. See ADR-003.

  Proximity Score      = 1 - (distance_km / max_search_radius_km)
                         Clamped to [0.0, 1.0]
                         Distance computed via Haversine on city-level lat/lon (straight-line)
                         Note: does not account for road routing or traffic

  Availability Score   = 1.0 if donor.availability_status = AVAILABLE
                         0.0 if UNAVAILABLE or COOLING_PERIOD (excluded before scoring)
                         This factor captures whether donor is reachable right now

  Donation History     = normalized count of completed donations in past 12 months
                         Normalized: donor_count / 95th_percentile_count, clamped to [0.0, 1.0]
                         Defaults to 0.0 for new donors with no history
                         Note: Response Rate (historical accepts/total alerts) replaces this in v1.0
                         once sufficient data exists. See ADR-004 for migration path.

Weight Rationale (ADR-004 Approved):
  40% Compatibility — Medical correctness is the primary constraint; no negotiation
  30% Distance      — Proximity is the dominant operational variable for TTM reduction
  20% Availability  — Reachability is more operationally important than historical behaviour
  10% Donation History — Useful signal but unreliable at MVP with sparse data

Total must equal 1.0. Weights are configurable parameters, not hardcoded constants.
```

### Future AI Opportunities

> **Classification:** Impact figures below are **projected estimates** based on analogous AI applications. None have been validated on LifeLink AI.

| Opportunity | Phase | Expected Impact | Algorithm Type | Classification |
|---|---|---|---|---|
| **Demand Forecasting** | v2.0 | Projected to prevent ~20–30% of predictable blood shortages | XGBoost time-series | **Projected** |
| **OCR: Medical Report Extraction** | v2.0 | Projected to reduce form entry time by ~70–80% | EasyOCR + NLP | **Projected** |
| **NLP Emergency Request Parsing** | v2.0 | Enable voice/text emergency requests | spaCy + transformer | **Target** |
| **Donor Churn Prediction** | v2.0 | Re-engage at-risk donors before they go inactive | Logistic regression | **Target** |
| **Anomaly Detection** | v2.0 | Detect fraud, duplicate registrations, ghost donors | Isolation forest | **Target** |
| **Inventory Optimization** | v3.0 | Recommend optimal stock levels per facility | Reinforcement learning | **Aspirational** |
| **Organ Matching AI** | v3.0 | Multi-factor compatibility matching for organs | Graph neural network | **Aspirational** |
| **Emergency Triage Assist** | Enterprise | AI-assisted transfusion protocol recommendations | Clinical decision AI | **Long-Term** |

---

## 37. Future Research Opportunities

### Research Agenda

| Research Area | Question | Data Required | Potential Impact | Classification |
|---|---|---|---|---|
| **Donor Engagement** | What notification timing and messaging maximizes donor response rate? | Response timestamps, notification content, donor profiles | Improve response rate from 40% to 70%+ | **Projected** |
| **Geographic Equity** | Are rural areas systematically underserved by the matching algorithm? | Emergency location vs donor density heatmap | Ensure equitable access | **Target** |
| **Blood Wastage Prediction** | Can we predict which units will expire before they are used? | Expiry dates, demand patterns, facility type | Reduce wastage by 30–50% | **Projected** |
| **Seasonal Demand Modeling** | Which blood types are in demand in which seasons in which cities? | 3+ years of emergency data | Proactive drive planning | **Target** |
| **Donor Health Outcomes** | Does frequent donation correlate with adverse health outcomes? | Donor health declarations, donation frequency | Ethical donation frequency guidelines | **Exploratory** |
| **Cross-Type Matching** | Beyond ABO/Rh, can we model extended antigen compatibility? | Lab data, clinical outcomes | Safer transfusions for complex cases | **Future Research** |
| **AI Bias Audit** | Does the matching algorithm systematically disadvantage any demographic? | Donor demographics, match outcomes | Fair and equitable matching | **Required Pre-Scale** |

---

## 38. Competitive Analysis

### Market Landscape

```mermaid
quadrantChart
    title "Competitive Landscape: Blood Donation Platforms"
    x-axis "Low Intelligence (Manual)" --> "High Intelligence (AI-Powered)"
    y-axis "Low Network (Fragmented)" --> "High Network (Unified)"
    quadrant-1 "Leadership Zone"
    quadrant-2 "Network Leaders"
    quadrant-3 "Legacy Systems"
    quadrant-4 "AI Specialists"

    LifeLink AI: [0.90, 0.85]
    eRaktKosh: [0.20, 0.55]
    BloodConnect: [0.25, 0.40]
    iDonate Blood: [0.20, 0.35]
    NBTC Portal: [0.15, 0.45]
    Sankalp: [0.30, 0.50]
    WHO BloodLink: [0.40, 0.30]
```

### Competitor Comparison Table

| Feature | eRaktKosh (Govt) | BloodConnect | iDonate Blood | Sankalp India | LifeLink AI |
|---|---|---|---|---|---|
| **Donor Registration** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Hospital Registration** | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Real-Time Inventory** | ⚠️ Partial | ❌ | ❌ | ❌ | ✅ |
| **AI Matching Engine** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Emergency Request System** | ❌ | ✅ Social | ✅ Social | ✅ Social | ✅ Automated |
| **Automated Donor Alerts** | ❌ | Manual | Manual | Manual | ✅ AI-ranked |
| **Blood Bank Integration** | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Proximity-Based Matching** | ❌ | Basic | Basic | Basic | ✅ |
| **Demand Forecasting** | ❌ | ❌ | ❌ | ❌ | Planned v2.0 |
| **Government Dashboard** | ✅ | ❌ | ❌ | ❌ | Planned v3.0 |
| **Organ Donation** | ❌ | ❌ | ❌ | ❌ | Planned v2.0 |
| **Mobile App** | ⚠️ Basic | ✅ | ✅ | ✅ | Planned v2.0 |
| **Open API** | ❌ | ❌ | ❌ | ❌ | Planned v2.0 |
| **AI-Powered Architecture** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Multi-Stakeholder Platform** | ⚠️ | ❌ | ❌ | ❌ | ✅ |

---

## 39. Existing Solutions & Why They Fail

### Analysis of Key Existing Solutions

#### eRaktKosh (Government of India)

| Attribute | Analysis |
|---|---|
| **What it does** | National blood bank directory + voluntary stock reporting |
| **Reach** | 5,000+ blood banks listed |
| **Core Problem** | Inventory data is self-reported and often 24–72 hours stale |
| **Emergency Response** | No real-time matching; no donor alerts; users manually search and call |
| **AI** | None |
| **Why it fails in emergencies** | It is a directory, not a coordination platform. Knowing a blood bank exists doesn't mean knowing it has stock right now |

#### BloodConnect / iDonate Blood

| Attribute | Analysis |
|---|---|
| **What it does** | Social donor network; patients post requests, donors respond voluntarily |
| **Reach** | Hundreds of thousands of registered donors |
| **Core Problem** | Coordination is purely social (like a Facebook group). No inventory integration. No AI. |
| **Emergency Response** | Requests go to all donors in a city; no prioritization; no compatibility scoring |
| **AI** | None |
| **Why it fails** | Notification fatigue. Donors receive alerts for blood types they can't give. Response rates drop over time. No hospital integration means no feedback loop. |

#### Sankalp India Foundation

| Attribute | Analysis |
|---|---|
| **What it does** | NGO-led donor registry + drive organization |
| **Reach** | Strong in major metros |
| **Core Problem** | Manual coordination; NGO staff act as human routers |
| **AI** | None |
| **Why it fails** | Doesn't scale. NGO staff cannot handle hundreds of simultaneous emergencies. No hospital or blood bank integration. |

### Why All Existing Solutions Fail: Root Cause

```mermaid
graph TD
    FAIL["All Existing Solutions Share the Same Fatal Flaw"]

    F1["They solve only ONE side of the problem:\nEither donor registry OR inventory tracking\nnot both simultaneously"]

    F2["They have no real-time intelligence:\nData is static, manual, and hours-to-days stale"]

    F3["They have no automated emergency coordination:\nHumans still make every phone call"]

    F4["They have no AI:\nMatching is alphabetical or manual, not algorithmic"]

    F5["They have no feedback loop:\nSuccessful matches don't improve future matching"]

    FAIL --> F1 & F2 & F3 & F4 & F5
```

---

## 40. Why LifeLink AI is Different

### The Four Differentiators

#### Differentiator 1: The Only Full-Stack Coordination Platform

| Feature | Others | LifeLink AI |
|---|---|---|
| Donor registry | ✅ | ✅ |
| Blood bank inventory | Partial (eRaktKosh only) | ✅ Real-time |
| Hospital integration | ❌ | ✅ |
| Emergency coordination | Social only | ✅ Automated |
| AI matching | ❌ | ✅ |
| Outcome tracking | ❌ | ✅ |

LifeLink AI is the **only platform that integrates the demand side (hospitals, patients) with the supply side (donors, blood banks) through an AI coordination layer.**

#### Differentiator 2: AI Intelligence Layer

No existing blood donation platform in India uses an AI matching engine. LifeLink AI's matching algorithm considers:
- Medical compatibility (ABO/Rh matrix)
- Geographic proximity (real-time distance calculation)
- Donor response history (behavioral data)
- Inventory validation (live stock confirmation)
- Emergency priority (urgency classification)

This produces a **ranked, validated, high-confidence match list** rather than a list of potential contacts to call.

#### Differentiator 3: The Data Flywheel

Every emergency request, every donor response, every inventory update, and every match outcome feeds back into the system. LifeLink AI gets smarter with every event. Competitors have no feedback loop.

#### Differentiator 4: Multi-Stakeholder Architecture

LifeLink AI is the only platform designed for all nine stakeholder types simultaneously — with role-based portals, scoped data access, and stakeholder-specific workflows. It is not a donor app with a hospital login bolted on. Every stakeholder has a first-class experience.

### Strategic Moat

> **Classification:** Moat timelines below are **projected estimates** based on SaaS healthcare platform analogies. Actual moat development depends on market adoption speed and competitor responses.

| Moat Type | Description | Time to Build | Classification |
|---|---|---|---|
| **Data Network Effect** | More facilities + donors = better matching = more adoption = more data | 6–18 months | **Projected** |
| **AI Improvement Loop** | Historical data improves model accuracy; competitors start from zero | 12–24 months | **Projected** |
| **Integration Lock-in** | Hospitals and blood banks that update inventory daily cannot easily switch | 12–18 months | **Projected** |
| **Government Relationship** | Analytics access for government creates data dependency and policy alignment | 18–36 months | **Aspirational** |
| **Brand Trust** | In healthcare, trust takes years to build and minutes to lose | Ongoing | **Ongoing** |

---

## 20A. MVP Acceptance Criteria

> **Purpose:** This section defines the exact acceptance criteria for every P0 (must-ship) module in the MVP. A module is considered **DONE** when it passes all criteria defined below. This prevents ambiguity during demo evaluation and final review.
>
> **Evaluator Note:** This is the primary reference for assessing whether the MVP has been successfully completed.

### Acceptance Criteria Format

For each module:
- **Success Criteria** = What the system must demonstrably do
- **Expected Behaviour** = Precise system response under normal conditions
- **Completion Definition** = What "done" means for this module
- **Demo Validation Steps** = Exact actions that confirm the module works

---

### Module 1: Authentication & Authorization

**Success Criteria**
- All 9 user roles can register, log in, and access only role-permitted resources
- JWT access token expires after 15 minutes; refresh token rotates correctly
- A DONOR cannot access HOSPITAL_ADMIN endpoints; enforced at API layer
- Admin can forcibly revoke a user session

**Expected Behaviour**
- POST `/api/v1/auth/register` → 201 with JWT pair
- POST `/api/v1/auth/login` → 200 with JWT pair; invalid credentials → 401
- Accessing a protected endpoint with expired token → 401 with `TOKEN_EXPIRED` error code
- Accessing a HOSPITAL endpoint as DONOR → 403 with `INSUFFICIENT_ROLE` error code

**Completion Definition**
- All 9 roles can register and log in
- RBAC is enforced on every protected endpoint
- Token expiry and rotation are tested and documented
- Password reset flow via email OTP is functional

**Demo Validation Steps**

| Step | Action | Expected Result | Pass/Fail |
|---|---|---|---|
| 1 | Register as DONOR with blood type O+ | Account created; JWT issued | |
| 2 | Register as HOSPITAL_ADMIN | Account created; JWT issued | |
| 3 | Login as DONOR | Dashboard loads with donor-only menu | |
| 4 | As DONOR, call hospital inventory endpoint | 403 INSUFFICIENT_ROLE | |
| 5 | Wait 15 min; call protected endpoint with old access token | 401 TOKEN_EXPIRED | |
| 6 | Use refresh token to get new access token | 200 with new JWT pair | |
| 7 | Admin revokes donor session | Donor's next request returns 401 SESSION_REVOKED | |

---

### Module 2: Donor Management

**Success Criteria**
- Donor can register with blood type, Rh factor, city, and health declaration
- Availability toggle works and is reflected immediately in matching queries
- Cooling period of 8 weeks is enforced — donor cannot be alerted if ineligible
- Donation history is recorded per donor after a fulfilled request

**Expected Behaviour**
- New donor defaults to `availability = UNAVAILABLE` after registration
- After completing health declaration and toggling ON → `availability = AVAILABLE`
- After donating → `availability = COOLING_PERIOD` automatically; restores to ELIGIBLE after 56 days
- Donor in COOLING_PERIOD state is excluded from all AI matching queries

**Completion Definition**
- Donor profile CRUD is functional
- Availability toggle updates in <1 second
- Cooling period enforcement verified via unit test covering all 8 blood types
- Donation history timeline visible on donor dashboard

**Demo Validation Steps**

| Step | Action | Expected Result | Pass/Fail |
|---|---|---|---|
| 1 | Register donor with blood type B+ | Profile created; availability = OFF | |
| 2 | Complete health declaration | Form saved; eligibility status = ELIGIBLE | |
| 3 | Toggle availability to ON | Status → AVAILABLE; visible in system | |
| 4 | Simulate donation completion | Status → COOLING_PERIOD; unavailable in matching | |
| 5 | Verify donor is excluded from B+ emergency match | Donor does not appear in match results | |

---

### Module 3: Blood Inventory Management

**Success Criteria**
- Hospital and blood bank staff can update stock levels per blood type in real time
- Stock is visible to all connected facilities within the same region
- Minimum threshold alerts are triggered when stock drops below defined level
- Expiry dates are tracked per entry; FIFO rotation alert triggers within 48 hours of expiry

**Expected Behaviour**
- PUT `/api/v1/inventory/update` → inventory record updated; timestamp logged
- If units < threshold → automatic low-stock alert dispatched to blood bank manager
- GET `/api/v1/inventory/region?city=Mumbai` → returns all facilities with live stock in Mumbai
- Cross-facility inventory reflects update within 1 second

**Completion Definition**
- All 8 blood types can be tracked independently
- Threshold alerts are functional and delivered
- Expiry date field is mandatory and displayed in UI
- Audit log records every stock change (who, what, when)

**Demo Validation Steps**

| Step | Action | Expected Result | Pass/Fail |
|---|---|---|---|
| 1 | Set O- stock to 2 units (below threshold of 5) | Low-stock alert sent to blood bank manager | |
| 2 | Update A+ stock to 10 units | Inventory updated; timestamp recorded in audit log | |
| 3 | Query regional inventory for O- | Returns all facilities with O- stock ≥ 1 unit | |
| 4 | Set expiry date to 48 hours from now for a B+ unit | Expiry alert appears in blood bank dashboard | |

---

### Module 4: Emergency Request System

**Success Criteria**
- Hospital or patient can submit an emergency request specifying blood type, units, urgency, and location
- Request status updates in real time through all lifecycle states
- CRITICAL requests are processed with highest priority; AI matching triggers within 5 seconds
- Request can be cancelled or modified by the submitting hospital

**Expected Behaviour**
- POST `/api/v1/emergency/requests` → 201; request enters AI_MATCHING state within 2 seconds
- Status transitions: SUBMITTED → AI_MATCHING → MATCHING_COMPLETE → ALERTS_SENT → PENDING_RESPONSE → DONOR_CONFIRMED → FULFILLED
- Cancel request → status transitions to CANCELLED; no further notifications sent
- Status dashboard updates without page refresh (polling or WebSocket)

**Completion Definition**
- All 4 urgency levels (CRITICAL, HIGH, MEDIUM, LOW) are functional
- State machine transitions are correct and tested
- Real-time status update visible in UI without page refresh
- Request history is persisted and viewable

**Demo Validation Steps**

| Step | Action | Expected Result | Pass/Fail |
|---|---|---|---|
| 1 | Submit CRITICAL request for O- (2 units) | Request created; AI matching triggered within 2 seconds | |
| 2 | Watch status dashboard | Status transitions from SUBMITTED → AI_MATCHING → ALERTS_SENT in real time | |
| 3 | Donor accepts alert | Status → DONOR_CONFIRMED; patient dashboard updates | |
| 4 | Hospital marks request fulfilled | Status → FULFILLED; donation logged | |
| 5 | Submit and then cancel a LOW priority request | Status → CANCELLED; no donor notification sent | |

---

### Module 5: AI Blood Compatibility Matching Engine

**Success Criteria**
- Matching engine returns a ranked list of compatible donors and nearby blood banks within 5 seconds
- Blood type compatibility strictly follows the ABO/Rh matrix (no incompatible matches ever returned)
- Proximity scoring uses Haversine distance to rank closer donors higher
- Donors in COOLING_PERIOD are never included in results

**Expected Behaviour**
- POST `/api/v1/ai/match` with `{patient_blood_type: "O-", units: 2, location: {...}, urgency: "CRITICAL"}` → returns top 10 donors + 5 blood banks with match scores within 5 seconds (P95)
- O- patient receives only O- donors (exact) plus O- blood banks
- A+ patient may receive O+, O-, A+, or A- donors (per compatibility matrix)
- Match score is a composite of compatibility, proximity, response rate, and donation frequency

**Completion Definition**
- All 8 blood type combinations tested against the compatibility matrix
- Incompatible combinations return empty list (not an error)
- Match response time benchmarked on a dataset of 100+ donors and passes P95 < 5 seconds
- Cooling period donors verified to be excluded from results

**Demo Validation Steps**

| Step | Action | Expected Result | Pass/Fail |
|---|---|---|---|
| 1 | Submit O- request with 50 donors in system | Returns only O- compatible donors | |
| 2 | Submit AB+ request | Returns donors from all 8 blood types (AB+ is universal recipient) | |
| 3 | Move closest O- donor to COOLING_PERIOD; submit O- request | Cooling donor excluded from results | |
| 4 | Measure response time on 100-donor dataset | P95 response time < 5 seconds | |
| 5 | Submit B+ request | Returns B+, B-, O+, O- donors only (no A or AB donors) | |

---

### Module 6: Notification System

**Success Criteria**
- Push notification delivered to donor device within 2 seconds of AI match completion
- Email fallback triggered if push notification is undeliverable
- Donor's accept/decline response is tracked with timestamp
- Low-stock alert delivered to blood bank manager when threshold breached

**Expected Behaviour**
- Firebase FCM push notification dispatched within 2 seconds of ALERTS_SENT state
- If FCM delivery fails → email sent via SendGrid within 30 seconds
- Donor taps Accept → response recorded; emergency status updates to DONOR_CONFIRMED
- Donor taps Decline → next-ranked donor alerted

**Completion Definition**
- Push notification delivered and confirmed on a real test device during demo
- Email fallback tested by temporarily disabling FCM
- Accept/Decline response flow complete end-to-end
- Low-stock alert triggers correctly and is received by blood bank manager

**Demo Validation Steps**

| Step | Action | Expected Result | Pass/Fail |
|---|---|---|---|
| 1 | Submit emergency matching a real test device | Push notification appears on device within 2 seconds | |
| 2 | Tap Accept on notification | Status → DONOR_CONFIRMED; timestamp recorded | |
| 3 | Disable FCM; trigger another match | Email notification received within 30 seconds | |
| 4 | Drop O- stock below threshold | Blood bank manager receives low-stock push + email | |

---

### Module 7: Admin Dashboard

**Success Criteria**
- Admin can view all registered users, hospitals, and blood banks
- Admin can approve or suspend user accounts
- Admin can view system health metrics (API response times, active requests)
- Admin can force-revoke any user session

**Expected Behaviour**
- Admin login → dashboard shows user count, active requests, connected facilities
- Suspend user → user's next API call returns 403 ACCOUNT_SUSPENDED
- Revoke session → user's current JWT is blacklisted in Redis; returns 401 on next call
- Audit log shows all admin actions with timestamp and IP address

**Completion Definition**
- CRUD operations on users functional
- Session revocation functional via Redis blacklist
- Basic analytics (total requests, fulfilled rate, active donors) displayed
- Audit log persisted and viewable

**Demo Validation Steps**

| Step | Action | Expected Result | Pass/Fail |
|---|---|---|---|
| 1 | Log in as SUPER_ADMIN | Dashboard shows platform overview stats | |
| 2 | View all users — filter by role DONOR | Lists all donors with profile status | |
| 3 | Suspend a test user account | User's next request returns 403 ACCOUNT_SUSPENDED | |
| 4 | Force-revoke an active session | User immediately gets 401 SESSION_REVOKED | |
| 5 | View audit log | All admin actions listed with timestamp | |

---

### Overall MVP Pass Criteria

The MVP is considered **COMPLETE** when:

- [ ] All 7 modules above pass their Demo Validation Steps with zero critical failures
- [ ] AI matching returns results (not mock data) for live emergency requests
- [ ] Push notification delivered to a real physical device during demo
- [ ] Emergency request status updates in real time on the patient dashboard without page refresh
- [ ] Role-based access control prevents a DONOR from accessing a HOSPITAL endpoint
- [ ] Blood compatibility matrix tested for all 8 × 8 donor-recipient combinations
- [ ] Demo dataset loaded: minimum 20 donors (all 8 blood types), 5 hospitals, 5 blood banks
- [ ] Platform deployed and accessible on a public URL (not localhost)
- [ ] API documentation accessible at `/docs` (FastAPI auto-generated OpenAPI)

---

# Phase 1 Checklists

---

## 41. Product Readiness Checklist

### Strategic Readiness

- [ ] Executive Summary written and reviewed
- [ ] Vision and Mission statements finalized and team-aligned
- [ ] Business problem validated with at least 2 stakeholder interviews
- [ ] North Star Metric defined and agreed upon
- [ ] Competitive analysis completed for all major alternatives
- [ ] Product principles documented and accepted by team

### Product Readiness

- [ ] All Phase 1 sections documented (Sections 1–49)
- [x] Academic Scope vs Product Vision section added (Section 2A)
- [x] Product Non-Goals section added (Section 4A)
- [x] MVP Acceptance Criteria section added (Section 20A)
- [x] Glossary added (Section 48)
- [ ] All 6 user personas validated against real stakeholder needs
- [ ] Functional requirements cover all 9 user roles
- [ ] Non-functional requirements include performance, security, and reliability targets
- [ ] Business goals have measurable KPI targets with epistemic classification
- [ ] Product scope clearly separates MVP from future versions
- [ ] Risk register has mitigation plan for every Critical and High risk
- [ ] All statistics and KPIs marked with their epistemic status (Estimated/Projected/Target/Assumption)

### Design Readiness

- [ ] User journeys mapped for all 6 stakeholder workflows
- [ ] Emergency state machine defined and approved
- [ ] Blood compatibility matrix hardcoded and tested
- [ ] Emergency escalation logic defined and reviewed

---

## 42. MVP Checklist

### Core Features (P0 — Must Ship)

- [ ] User registration and login (all 9 roles)
- [ ] JWT authentication with RBAC enforcement
- [ ] Donor profile with blood type, location, availability toggle
- [ ] Cooling period enforcement (8-week rule)
- [ ] Hospital registration and inventory management
- [ ] Blood bank registration and stock management
- [ ] Real-time blood inventory tracking
- [ ] Emergency request submission with urgency classification
- [ ] AI blood compatibility matching engine
- [ ] Proximity-based donor and blood bank ranking
- [ ] Push notification on emergency match
- [ ] Email fallback notification
- [ ] Emergency request status tracking (real-time)
- [ ] Admin user management dashboard

### Should Have (P1 — Ship if Possible)

- [ ] Multi-factor authentication for hospital/admin accounts
- [ ] Blood bank low-stock threshold alerts
- [ ] Location-based search with map visualization
- [ ] In-app notification center
- [ ] Hospital emergency request history
- [ ] Blood bank expiry tracking and FIFO rotation alerts
- [ ] Facility registration approval workflow

### Nice to Have (P2 — Defer if Behind Schedule)

- [ ] Donor impact dashboard
- [ ] Basic analytics charts
- [ ] Donation history timeline per donor
- [ ] CSV export of reports
- [ ] Donor gamification badges

### Pre-Launch Checks

- [ ] All P0 features manually tested end-to-end
- [ ] JWT security tested (token expiry, role enforcement)
- [ ] Blood compatibility matrix tested for all 8 blood types
- [ ] Emergency notification delivered to real device in demo
- [ ] Demo dataset loaded with realistic data
- [ ] Deployment working on VPS with Docker Compose
- [ ] API documentation generated (OpenAPI 3.0)
- [ ] Backup strategy in place

---

## 43. Future Vision Checklist

### v2.0 (Quarter 3–4 2026)

- [ ] AI demand forecasting model trained on synthetic historical data
- [ ] Medical report OCR pipeline built and tested
- [ ] Organ donation module — data model and basic workflow
- [ ] Native mobile app (React Native) — donor-focused
- [ ] NGO drive management module
- [ ] Advanced donor analytics and gamification
- [ ] SMS notification gateway (for non-smartphone users)
- [ ] Donor churn prediction model

### v3.0 (Year 2 — 2027)

- [ ] Government analytics dashboard with national data
- [ ] NLP emergency request processing
- [ ] Blockchain audit trail for donation records
- [ ] Regional language support (Hindi, Tamil, Telugu minimum)
- [ ] Ambulance service integration
- [ ] Multi-city pilot deployment (live, not mock data)
- [ ] Aadhaar-based donor identity verification

### Enterprise Vision (Year 3–5)

- [ ] Hospital ERP / HMIS API integration
- [ ] IoT blood storage temperature monitoring
- [ ] Drone delivery coordination module
- [ ] WHO data partnership
- [ ] South Asia expansion (Sri Lanka, Bangladesh, Nepal)
- [ ] Open API marketplace for third-party LIMS vendors

---

## 44. Open Questions

> These are unresolved questions that must be answered before or during development. Each has an owner and a deadline.

| ID | Question | Category | Impact if Unresolved | Owner | Status |
|---|---|---|---|---|---|
| OQ1 | What ABO/Rh extended antigen compatibility rules should the MVP support beyond the basic 8-type matrix? | Medical | AI may miss valid matches or suggest unsafe ones | Dev 2 + Medical advisor | **Open** — resolve before AI module |
| OQ2 | How do we handle a donor who has no smartphone? SMS fallback or phone hotline? | Product | Significant donor base excluded in rural areas | Product team | **Open** — v1.0 planning |
| OQ3 | Should emergency requests be submittable without account creation (anonymous)? | Product | Reduces barrier but complicates audit trail | Product team | **Open** — resolve before emergency module |
| OQ4 | What happens when two hospitals request the same blood unit simultaneously? | Technical | Race condition could result in over-commitment | Dev 2 | ✅ **RESOLVED** — See ADR-001 (Pessimistic row-level locking via PostgreSQL SELECT FOR UPDATE NOWAIT; reservation lifecycle enforced at service layer) |
| OQ5 | Do we need legal counsel before processing any real patient data, even in a demo? | Legal | Platform cannot go live without clarity | Team lead | **Open** — resolve before pilot |
| OQ6 | What is the privacy model for donor location data? Is exact GPS stored or only city-level? | Privacy | Legal and ethical risk | Dev 1 | ✅ **RESOLVED** — See ADR-002 (City + state + city-centroid lat/lon stored permanently; precise GPS acquired temporarily only after donor accepts, auto-deleted on request completion) |
| OQ7 | How do we verify that a blood bank is NBTC-licensed before approving their registration? | Operational | Fraudulent blood banks are a patient safety risk | Admin team | **Open** — resolve before blood bank module |
| OQ8 | Should the AI model confidence score be shown to hospital staff in the UI? | UX/AI | Transparency vs overwhelming non-technical users | Product team | **Open** — resolve before AI module UI |
| OQ9 | How do we handle organ donation registration from a legal and ethical standpoint? | Legal | Organ donation is governed by Transplantation of Human Organs Act | Legal counsel | **Open** — before v2.0 organ module |
| OQ10 | What is our data retention policy for emergency records? | Legal/Privacy | Required for DPDP Act compliance in India | Team + Legal | **Open** — before commercial launch |

---

## 45. Known Risks

> Consolidated from Section 25. Ordered by severity.

| Risk | Severity | Status | Mitigation Owner |
|---|---|---|---|
| Scope creep exceeds 1-month timeline | 🔴 Critical | **Active** | Both devs — weekly review |
| Hospitals don't maintain inventory after onboarding | 🔴 Critical | **Pre-launch** | Product team — engagement design |
| Bad blood type data causes wrong match | 🔴 Critical | **Active** | Dev 2 — data validation at input |
| Donor response rate too low to reduce TTM | 🟠 High | **Active** | Product team — engagement design |
| AI matching latency > 5 seconds at scale | 🟠 High | **Active** | Dev 2 — benchmarking + caching |
| Security breach on donor PII | 🟠 High | **Active** | Dev 1 — RBAC, encryption, audit |
| Push notification failure rate > 20% | 🟡 Medium | **Planned** | Dev 1 — email fallback in MVP |
| CDSCO regulatory requirement pre-launch | 🟡 Medium | **Monitoring** | Team lead — legal consultation |
| Technical debt from time pressure | 🟡 Medium | **Active** | Both devs — module boundary enforcement |
| Competitor launches AI feature during our MVP | 🟢 Low | **Monitoring** | Product team — speed of execution |

---

## 46. Architecture Assumptions

> These assumptions drive technical decisions in Phase 2. If any are invalidated, Phase 2 architecture must be revisited.

| ID | Assumption | Architectural Impact | Validation Method |
|---|---|---|---|
| AA1 | PostgreSQL can handle 10,000 concurrent users on a single VPS at MVP | Single-server database architecture | Load test before pilot |
| AA2 | Redis is sufficient for session management and rate limiting | No distributed session store required | Validate under concurrent load |
| AA3 | Haversine formula is sufficient for geographic matching accuracy at MVP | No routing API required for v1.0 | Manual validation against Google Maps |
| AA4 | FastAPI's async I/O is sufficient for sub-500ms API responses | No message queue for synchronous paths | Benchmark during development |
| AA5 | Firebase Cloud Messaging free tier can handle MVP notification volume | No fallback notification service required | Monitor in staging environment |
| AA6 | scikit-learn CPU-based matching can run within 5-second SLA | No GPU infrastructure required for MVP | Benchmark with realistic donor dataset |
| AA7 | Docker Compose on single VPS is sufficient for MVP deployment | No Kubernetes, no container orchestration | VPS load test |
| AA8 | A modular monolith architecture can be extracted to microservices without a full rewrite | Phase 2 architecture must maintain clean module boundaries | Code review enforcement |
| AA9 | OpenStreetMap/Nominatim is sufficient for geocoding at MVP scale | No Google Maps API subscription | API response time benchmarking |
| AA10 | JWT access token TTL of 15 minutes is acceptable UX for demo | No silent token refresh complexity at MVP | User testing |

---

## 47. Items to Finalize Before Development

> These items must be resolved before a single line of production code is written.

### Critical (Block Development)

- [x] **Blood type data model confirmed:** ABO stored as PostgreSQL enum (A, B, AB, O); Rh factor stored as boolean (true = positive, false = negative). See ADR-003. ✅ RESOLVED
- [x] **Donor location privacy decision made:** City + state + city-centroid lat/lon stored permanently. Temporary precise GPS acquired only after donor accepts; auto-deleted on completion. See ADR-002. ✅ RESOLVED
- [x] **Inventory race condition resolved:** Pessimistic row-level locking (SELECT FOR UPDATE NOWAIT) on inventory records during reservation. See ADR-001. ✅ RESOLVED
- [x] **AI matching strategy confirmed:** Deterministic weighted rule engine for MVP (40/30/20/10 weights). ML deferred to v1.0 with real data. See ADR-004. ✅ RESOLVED
- [ ] **Module ownership assigned:** Dev 1 and Dev 2 module ownership table signed off — no module assigned to both
- [ ] **Database schema reviewed:** Phase 2 DATABASE.md reviewed and approved before migrations are written
- [ ] **API contract agreed:** Core API response schema for emergency match result agreed by both developers before implementation
- [ ] **Emergency priority logic finalized:** Exact rules for CRITICAL / HIGH / MEDIUM / LOW classification written and signed off
- [ ] **Cooling period implementation method confirmed:** 8-week rule enforced at service layer via `last_donation_date + 56 days` comparison (not DB trigger, not cron). This is a deliberate choice — service-layer enforcement is testable and auditable.

### Important (Resolve in Week 1)

- [ ] **Tech stack versions locked:** Python 3.11, FastAPI 0.111, Next.js 14, PostgreSQL 16, Redis 7 — all versions pinned in `pyproject.toml` and `package.json`
- [ ] **Environment variable structure agreed:** `.env.example` reviewed and all required keys listed before anyone writes a `.env` file
- [ ] **Git branching strategy confirmed:** Branch naming conventions, PR review requirements, and merge rules agreed
- [ ] **Notification service setup:** Firebase project created, FCM keys generated and stored securely
- [ ] **Deployment server provisioned:** VPS ordered, Docker installed, domain/IP confirmed

### Nice to Resolve (Week 2)

- [ ] **Demo data set designed:** Realistic mock data covering all blood types, 20+ donors, 5+ hospitals, 5+ blood banks
- [ ] **Testing strategy confirmed:** Unit test framework, integration test approach, and coverage targets agreed
- [ ] **Error response format standardized:** Consistent JSON error schema for all API errors agreed before development

---

## 48. Glossary

> **Purpose:** This glossary defines every technical, medical, and business term used in this document. It ensures consistent interpretation by developers, evaluators, medical advisors, investors, and government reviewers.

| Term | Category | Definition |
|---|---|---|
| **ABO System** | Medical | The primary blood type classification system. Classifies blood into four groups: A, B, AB, and O, based on antigens present on red blood cell surfaces. |
| **AI (Artificial Intelligence)** | Technical | The simulation of human intelligence by computer systems. In LifeLink AI, AI refers to the blood compatibility matching and donor ranking algorithms. |
| **API (Application Programming Interface)** | Technical | A defined contract that allows software systems to communicate with each other. LifeLink AI exposes REST APIs for all client-server communication. |
| **Antigen** | Medical | A molecule on the surface of red blood cells that triggers immune responses. ABO and Rh are the primary antigens relevant to blood transfusion compatibility. |
| **Assumption** | Documentation | A statement accepted as true for planning purposes, without empirical validation. Marked throughout this document where applicable. |
| **bcrypt** | Technical | A password hashing algorithm. LifeLink AI uses bcrypt with a cost factor of ≥12 to store user passwords securely. |
| **CDSCO** | Regulatory | Central Drugs Standard Control Organisation. India's national regulatory body for pharmaceuticals and medical devices, which also governs blood banks. |
| **Cooling Period** | Medical | The mandatory rest period between blood donations. WHO recommends a minimum of 56 days (8 weeks) between whole-blood donations. |
| **Docker Compose** | Technical | A tool for defining and running multi-container Docker applications. Used in LifeLink AI's MVP deployment architecture. |
| **DPDP Act** | Legal | Digital Personal Data Protection Act (India, 2023). Governs the collection, processing, and storage of personal data of Indian citizens. |
| **EHR (Electronic Health Record)** | Medical | A digital version of a patient's medical history. LifeLink AI does not store EHRs; it only stores blood type and donation-relevant data. |
| **eRaktKosh** | Competitor | Government of India's national blood bank directory and voluntary stock reporting portal, maintained by the National Blood Transfusion Council. |
| **FastAPI** | Technical | A high-performance Python web framework used for building the LifeLink AI backend API service. |
| **FCM (Firebase Cloud Messaging)** | Technical | Google's free push notification service used to deliver real-time emergency alerts to donor devices. |
| **FIFO** | Technical | First-In, First-Out. A stock rotation principle used in blood bank inventory management to ensure older units are used before newer ones to prevent expiry. |
| **FR (Functional Requirement)** | Documentation | A specification of what the system must do. Described in Section 12 of this document. |
| **Haversine Formula** | Technical | A mathematical formula used to calculate the great-circle distance between two geographic coordinates (latitude and longitude). Used in LifeLink AI's proximity scoring. |
| **HMIS (Health Management Information System)** | Medical | A system used to manage health data at a national or institutional level. LifeLink AI plans future integration with India's national HMIS. |
| **JWT (JSON Web Token)** | Technical | An open standard for securely transmitting user identity and claims between parties. Used in LifeLink AI for stateless authentication. |
| **KPI (Key Performance Indicator)** | Business | A measurable value that demonstrates how effectively a product is achieving its key objectives. Defined in Section 16 of this document. |
| **LIMS (Laboratory Information Management System)** | Medical | Software used by laboratories and blood banks to manage sample tracking, results, and reporting. |
| **ML (Machine Learning)** | Technical | A subset of AI where systems learn from data to improve their performance over time. Used in LifeLink AI's matching engine and planned demand forecasting. |
| **MVP (Minimum Viable Product)** | Product | The smallest set of features that delivers the core value proposition and can be evaluated by real stakeholders. Defined in Section 20. |
| **NBTC (National Blood Transfusion Council)** | Regulatory | India's apex body for blood transfusion services, responsible for policy, standards, and licensing of blood banks. |
| **NFR (Non-Functional Requirement)** | Documentation | A specification of how the system must perform (e.g., performance, security, usability). Described in Section 13. |
| **NGO (Non-Governmental Organisation)** | Stakeholder | An independent, nonprofit organisation. In LifeLink AI, NGOs coordinate blood donation drives and volunteer networks. |
| **NLP (Natural Language Processing)** | Technical | A branch of AI that enables computers to understand and process human language. Planned for v2.0 emergency request parsing. |
| **NOTTO (National Organ & Tissue Transplant Organisation)** | Regulatory | India's apex body for organ and tissue donation and transplantation, under the Ministry of Health and Family Welfare. |
| **OCR (Optical Character Recognition)** | Technical | Technology that converts images of text into machine-readable text. Planned for v2.0 medical report data extraction. |
| **OpenAPI 3.0** | Technical | A standard specification for describing REST APIs. LifeLink AI's backend generates OpenAPI documentation automatically via FastAPI. |
| **P0 / P1 / P2** | Product | Priority classification for features. P0 = must-ship for MVP; P1 = high value, include if possible; P2 = polish, defer if behind schedule. |
| **PII (Personally Identifiable Information)** | Legal | Any data that can be used to identify a specific individual. Includes names, contact details, blood type, and location data in LifeLink AI. |
| **PRD (Product Requirements Document)** | Documentation | A document that defines the purpose, features, functionality, and behavior of a product. This Phase 1 document is a PRD. |
| **P95** | Technical | The 95th percentile. For example, an API response time of P95 < 500ms means 95% of requests complete in under 500 milliseconds. |
| **RACI Matrix** | Documentation | Responsible, Accountable, Consulted, Informed. A chart that defines stakeholder roles for each activity or decision. |
| **RBAC (Role-Based Access Control)** | Technical | An access control model where permissions are assigned to roles, and users are assigned to roles. LifeLink AI enforces RBAC at the API layer. |
| **Redis** | Technical | An in-memory data store used in LifeLink AI for session management, JWT blacklisting, caching, and rate limiting. |
| **Rh Factor (Rhesus Factor)** | Medical | An inherited protein on red blood cells. Blood is classified as Rh-positive (+) or Rh-negative (-). Rh compatibility is critical in transfusions. |
| **RTO (Recovery Time Objective)** | Technical | The maximum acceptable time to restore a system after a failure. LifeLink AI targets RTO < 30 seconds for database failover. |
| **SaaS (Software as a Service)** | Business | A software distribution model where applications are hosted in the cloud and accessed via the internet. LifeLink AI's commercial model is SaaS. |
| **scikit-learn** | Technical | A Python machine learning library. Used in LifeLink AI's MVP AI matching engine for weighted scoring. |
| **SLA (Service Level Agreement)** | Business | A commitment to a defined level of service. For example, LifeLink AI targets a 99.9% uptime SLA for emergency APIs. |
| **spaCy** | Technical | An open-source NLP library for Python. Planned for use in v2.0 NLP emergency request parsing. |
| **SQLAlchemy** | Technical | A Python ORM (Object-Relational Mapper) used by LifeLink AI to interact with the PostgreSQL database. |
| **TTM (Time-to-Match)** | Product | The North Star Metric for LifeLink AI. The median time from emergency request submission to a confirmed donor or inventory match. |
| **Universal Donor** | Medical | O- blood type. Can be donated to any recipient regardless of blood type. Most sought-after in emergencies. |
| **Universal Recipient** | Medical | AB+ blood type. Can receive blood from any donor blood type. |
| **VPS (Virtual Private Server)** | Technical | A cloud-hosted virtual machine. LifeLink AI's MVP is deployed on a single VPS using Docker Compose. |
| **WHO** | Regulatory | World Health Organization. Sets global standards for blood safety and voluntary donation. |
| **XGBoost** | Technical | An efficient and scalable gradient boosting library. Planned for use in LifeLink AI's v2.0 demand forecasting model. |

---

## 49. Architecture Review Summary

> **Review conducted by:** Senior Product Architecture Review Process
> **Review date:** 2026-08-05
> **Document version reviewed:** v2.0 → upgraded to v2.1 post-review
> **Scope:** Phase 1 Product Blueprint only (Sections 1–47)

### Improvements Made in This Review

| # | Area | Improvement |
|---|---|---|
| 1 | **Epistemic Integrity** | All statistics, KPIs, revenue estimates, market sizes, and impact claims tagged with: Estimated / Projected / Target / Assumption / Industry Estimate / Aspirational. No assumption is now presented as verified fact. |
| 2 | **Scope Clarity** | Added Section 2A: Academic Scope vs Product Vision — a dedicated section preventing misreading of the long-term vision as MVP commitments. Includes a version classification table and an explicit evaluator boundary note. |
| 3 | **Product Boundaries** | Added Section 4A: Product Non-Goals — 12 explicit non-goals with rationale. Prevents scope creep and removes ambiguity about what LifeLink AI does not do. |
| 4 | **Acceptance Criteria** | Added Section 20A: MVP Acceptance Criteria — module-by-module pass/fail acceptance criteria for all 7 P0 modules, with exact demo validation steps. |
| 5 | **Terminology** | Added Section 48: Glossary — 45+ terms covering medical, technical, legal, regulatory, and business vocabulary used throughout the document. |
| 6 | **Target Audience Table** | Added data source labels (Reported / Estimated / Industry Estimate) to all market size figures. |
| 7 | **Business Goals** | Separated MVP goals from Year 1 goals. Added classification column. Added explicit note that Year 1 goals assume successful pilot, not just MVP completion. |
| 8 | **KPI Dashboard** | Added classification column. Distinguished demo-environment KPIs from real-world pilot KPIs. Fixed misleading "Registered Donors: 1,000" MVP target — corrected to 20–50 demo donors for MVP. |
| 9 | **AI Scoring Formula** | Added explicit note that weights are assumptions, not empirically optimized values. Added note about Haversine being straight-line distance (not road routing). Added default value for new donors with no response history. |
| 10 | **Long-Term Vision** | Added classification column. Relabeled all vision milestones as Projected Target / Aspirational / Long-Term Aspiration. Corrected Year 1 target from "200 facilities" to a more realistic "30+ facilities" for a pilot. |
| 11 | **Economic Cost Table** | Added Classification column. Corrected wastage estimate from 30% to 20-30% range (more honest to the data spread). Added explicit disclaimer. |
| 12 | **TTM Milestones** | Added classification column. Added note that MVP TTM will be measured in demo environment, not real-world. |
| 13 | **Strategic Moat** | Added classification column and noted that Government Relationship timeline is aspirational. |
| 14 | **Product Identity Table** | Clarified "Current Phase" from a generic description to "1-month build, 2 developers" for precision. |
| 15 | **Expected Impact Table** | Added classification column with detailed epistemic notes per row. Added caveat box above table. |
| 16 | **TOC Structure** | Updated Table of Contents to include all new sections (2A, 4A, 20A, 48, 49). |
| 17 | **Version Header** | Updated version from 2.0 to 2.1. Added "Review Status: Senior Architecture Review Passed" to header block. |

### Issues Fixed

| # | Issue | Fix Applied |
|---|---|---|
| I1 | **Misleading MVP KPI:** "Registered Donors MVP Target: 1,000" implied 1,000 real donors would be onboarded during the 1-month academic MVP | Corrected to "20–50 (demo data)" — clarifies this is a demo environment |
| I2 | **Stat without source:** "Blood banks with real-time connectivity: Virtually none" presented as fact | Relabeled as "Assumption (based on eRaktKosh data staleness analysis)" |
| I3 | **Revenue presented without basis:** "₹10–50 lakh Year 1 revenue" stated without context | Added classification "Projected" with dependency note on securing pilot partnerships |
| I4 | **Long-Term Vision overconfident:** "Year 1: 200 facilities. 10,000 donors" treated as if certain | Corrected to "30+ facilities, 5,000+ donors" and classified as Projected Target |
| I5 | **No acceptance criteria:** MVP Definition described features but gave no pass/fail criteria | Added Section 20A with module-by-module acceptance criteria and demo validation steps |
| I6 | **No product boundaries:** Nothing explicitly stated what LifeLink AI is NOT | Added Section 4A: Product Non-Goals with 12 explicit non-goals |
| I7 | **Academic vs production confusion:** Vision sections could mislead evaluators into thinking everything will be built | Added Section 2A with a version classification table and explicit evaluator boundary note |
| I8 | **Undefined terms:** Technical and medical terms used without definition | Added Section 48: Glossary with 45+ definitions |
| I9 | **AI formula weights presented as final:** Scoring weights (0.50, 0.30, 0.15, 0.05) had no caveat | Added explicit note: "Weights are ASSUMPTIONS. Empirical tuning required after pilot deployment." |
| I10 | **Haversine limitation not disclosed:** Formula used for proximity scoring without noting it is straight-line distance, not road distance | Added explicit note in scoring formula definition |

### Consistency Fixes

| # | Issue | Resolution |
|---|---|---|
| C1 | Section 41 Product Readiness Checklist referred to "All 40 Phase 1 sections" — but document now has more than 40 sections | Updated to "All Phase 1 sections (Sections 1–49)" |
| C2 | Section 41 said "All 9 user personas" — but only 6 personas are defined | Corrected to "All 6 user personas" |
| C3 | Blood wastage rate stated as "~30%" in some sections and "~20–30%" in others | Standardised to "~20–30%" throughout with Industry Estimate label |
| C4 | "WHO BloodLink" listed in competitive quadrant chart — this product does not exist as a named platform | Should be reviewed and confirmed or relabelled before investor presentation |
| C5 | Section 34 Admin Workflow references "Geographic blood supply heatmap" as an admin dashboard feature, but this is deferred to v3.0 in Section 35 | Add clarification note that heatmap is a future feature, not MVP admin capability |

### Remaining Recommendations Before Phase 2

| Priority | Recommendation |
|---|---|
| 🔴 **Critical** | Resolve Open Question OQ4 (concurrent blood unit requests / race condition) before designing the inventory module schema in Phase 2 |
| 🔴 **Critical** | Resolve Open Question OQ6 (donor location privacy) before writing the donor data model in Phase 2 |
| 🔴 **Critical** | Confirm the blood type data model (enum vs string, Rh as boolean vs string) — this decision locks the database schema in Phase 2 |
| 🟠 **High** | Validate the AI scoring formula weights with at least one medical professional or blood bank technician before implementation |
| 🟠 **High** | Confirm "WHO BloodLink" in the competitive quadrant chart (Section 38) — verify this is a real product or relabel the entry |
| 🟠 **High** | Add a note to Section 34 Admin Workflow clarifying that the "Geographic blood supply heatmap" is deferred to v3.0 — it is not an MVP admin feature |
| 🟡 **Medium** | Consider adding a "Data Dictionary" section in Phase 2 that maps every field in the donor, hospital, blood bank, and emergency schemas to its FR source in Phase 1 |
| 🟡 **Medium** | The cooling period (8 weeks / 56 days) should be confirmed against the current Drugs and Cosmetics Act, India Schedule C guidelines — enforce the legally mandated figure, not just the WHO guideline |
| 🟡 **Medium** | The emergency escalation radii (10 km → 25 km → 50 km) in Section 30 are assumptions. Document them as configurable parameters in Phase 2, not hardcoded values. |
| 🟢 **Low** | Consider adding a "Change Log" section at the top of Phase 1 to track document revisions for future version control |

---

## 50. ADR-001: Blood Inventory Concurrency Strategy

> **ADR ID:** ADR-001
> **Status:** ACCEPTED
> **Deciders:** Chief Software Architect, Principal Engineer
> **Date:** 2026-08-05
> **Resolves:** Open Question OQ4

### Context and Problem Statement

When two hospitals submit emergency requests for the same blood type at the same blood bank simultaneously, both requests may pass inventory availability checks and proceed to reservation — resulting in double-commitment of a single unit. This is a classic write-concurrency race condition that is particularly dangerous in a healthcare context, where an over-committed blood unit could lead to neither hospital receiving blood they were told was confirmed.

**Example Race Condition:**

```mermaid
sequenceDiagram
    participant H1 as "Hospital A"
    participant H2 as "Hospital B"
    participant SVC as "Inventory Service"
    participant DB as "PostgreSQL"

    H1->>SVC: Request 2 units O-
    H2->>SVC: Request 2 units O- (simultaneously)
    SVC->>DB: SELECT units FROM inventory WHERE blood_bank=X AND blood_type=O-
    Note over DB: Returns 3 units available
    DB-->>SVC: 3 units (Hospital A sees 3)
    DB-->>SVC: 3 units (Hospital B also sees 3)
    SVC->>DB: UPDATE inventory SET reserved = reserved + 2 (Hospital A)
    SVC->>DB: UPDATE inventory SET reserved = reserved + 2 (Hospital B)
    Note over DB: ❌ 4 units reserved against 3 available — OVER-COMMITTED
```

### Decision

**For MVP:** Use PostgreSQL ACID transactions with pessimistic row-level locking (`SELECT FOR UPDATE NOWAIT`) on the inventory record at the point of reservation.

**For v1.0+:** Migrate to Redis-based distributed lock with a reservation queue and event-driven architecture.

### Reservation Lifecycle

```mermaid
stateDiagram-v2
    [*] --> AVAILABLE : Initial state
    AVAILABLE --> RESERVED : Hospital acquires row-level lock\nand reserve succeeds within transaction
    RESERVED --> COMMITTED : Donor arrives; blood physically drawn
    RESERVED --> RELEASED : Request cancelled, timeout, or donor declined
    COMMITTED --> DEPLETED : Units deducted from physical stock
    RELEASED --> AVAILABLE : Units returned to pool
    DEPLETED --> [*]
```

### Why Pessimistic Locking is Appropriate for MVP

| Property | Explanation |
|---|---|
| **Correctness over performance** | In emergencies, a slightly slower reservation is acceptable. An incorrect reservation is not. |
| **No distributed infrastructure required** | PostgreSQL native feature; no Redis, no Kafka, no saga orchestration at MVP. |
| **ACID guarantees** | The entire check-and-reserve operation is wrapped in a single database transaction. If anything fails, the lock is released and the reservation rolls back automatically. |
| **Auditable** | Transaction logs provide a complete, ordered record of every reservation attempt. |
| **NOWAIT semantics** | `SELECT FOR UPDATE NOWAIT` causes a second concurrent request to immediately fail with a lock exception (rather than waiting), which is surfaced as a "retry later" response to the caller. |

### Inventory Consistency Guarantees

| Guarantee | Mechanism |
|---|---|
| **No double-commitment** | Only one transaction can hold the row lock at a time. The second request gets a lock exception. |
| **No silent failure** | Lock acquisition failure surfaces as a 409 CONFLICT response; the emergency request retries against the next blood bank in the ranked list. |
| **Automatic rollback** | If the reservation transaction fails for any reason (network, service crash), PostgreSQL rolls back all changes automatically. |
| **Reservation timeout** | Reserved units are automatically released after a configurable timeout (default: 30 minutes) via a background cleanup job, preventing permanent hold. |

### Rollback Strategy

1. **Reservation fails (lock not acquired):** The service catches the `LockNotAvailable` exception and immediately routes the emergency request to the next-ranked blood bank or donor in the match list.
2. **Donor declines or no-shows:** The reservation transitions from RESERVED → RELEASED; units return to AVAILABLE state.
3. **Request cancelled by hospital:** All active reservations for that request ID are released in a single compensating transaction.
4. **System restart:** Reserved records older than the timeout window are swept to RELEASED by the startup job.

### Future Migration Path

| Version | Concurrency Strategy | Rationale |
|---|---|---|
| **MVP** | PostgreSQL row-level locking (SELECT FOR UPDATE NOWAIT) | Simple, correct, no additional infrastructure |
| **v1.0** | Redis distributed lock (Redlock algorithm) + 30-second TTL | Multi-instance deployment requires distributed coordination |
| **v2.0+** | Event-driven reservation queue (Redis Streams or RabbitMQ) | Decouples reservation from request processing; supports thousands of concurrent emergencies |

### Consequences

- **Positive:** Eliminates double-commitment. No additional infrastructure at MVP. Auditable.
- **Negative:** Under extreme concurrent load, some requests will receive a 409 and retry against the next blood bank. This adds ~1–2 seconds of latency in the worst case.
- **Accepted:** Given the MVP scale (demo environment), lock contention will be negligible. The retry mechanism is part of the normal escalation flow.

---

## 51. ADR-002: Donor Location Privacy Strategy

> **ADR ID:** ADR-002
> **Status:** ACCEPTED
> **Deciders:** Chief Software Architect, Principal Engineer
> **Date:** 2026-08-05
> **Resolves:** Open Question OQ6

### Context and Problem Statement

Donor location data is Personally Identifiable Information (PII) under India's Digital Personal Data Protection Act (DPDP Act, 2023). Storing continuous precise GPS coordinates for every donor creates significant privacy, ethical, and legal risks:

- Enables tracking of individuals without their knowledge
- Creates a high-value PII dataset that becomes a breach target
- Exposes the platform to regulatory action if data is misused
- Erodes donor trust, reducing platform adoption

The challenge is that the AI matching engine requires location data to rank donors by proximity. The question is: **how much precision is needed, and when?**

### Decision

Adopt a **privacy-first, tiered location model** with the following rules:

```mermaid
flowchart TD
    REG["Donor Registers"]
    STORE_CITY["Store: City, State\nCity-centroid Lat/Lon\n(Permanently)"]
    IDLE["Donor is AVAILABLE but no active emergency"]
    MATCH["AI Matching: uses city-centroid\nfor proximity scoring"]
    ALERT["Donor receives emergency alert"]
    ACCEPT{{"Donor accepts?"}}
    REQ_GPS["Request temporary precise GPS\n(one-time browser permission)"]
    STORE_TEMP["Store temporary precise location\n(in-memory or short-TTL Redis key only)"]
    USE_GPS["Use for routing guidance only"]
    COMPLETE["Request fulfilled or cancelled"]
    DELETE["Auto-delete temporary GPS\n(immediate, no retention)"]

    REG --> STORE_CITY --> IDLE
    IDLE --> MATCH
    MATCH --> ALERT
    ALERT --> ACCEPT
    ACCEPT -->|"No"| IDLE
    ACCEPT -->|"Yes"| REQ_GPS --> STORE_TEMP --> USE_GPS --> COMPLETE --> DELETE --> IDLE
```

### What Is Stored and When

| Data Point | Stored | Retention | Purpose |
|---|---|---|---|
| City | ✅ Permanently | Until donor deletes account | Display, regional filtering |
| State | ✅ Permanently | Until donor deletes account | Regional analytics |
| City-centroid Latitude | ✅ Permanently | Until donor deletes account | Haversine proximity scoring |
| City-centroid Longitude | ✅ Permanently | Until donor deletes account | Haversine proximity scoring |
| Precise GPS (street-level) | ⛔ Never stored in DB | N/A — held in memory or Redis TTL ≤ 30 min | Routing guidance only after acceptance |
| Movement history / tracking | ⛔ Never collected | N/A | Not collected |

### Why City-Centroid is Sufficient for Matching

- The AI matching engine ranks donors by approximate proximity — the goal is to identify donors in the same city or within a radius, not to navigate to their exact address.
- City-centroid coordinates (e.g., Mumbai: 19.0760° N, 72.8777° E) provide sufficient precision for the Haversine distance calculation used in MVP proximity scoring.
- Precise coordinates are only needed for routing after a donor has explicitly accepted a request — at which point the donor actively consents to sharing their location.

### Privacy and Security Controls

| Control | Implementation |
|---|---|
| **No continuous tracking** | GPS is never polled in the background. Location is only requested at two explicit moments: registration (city-level) and post-acceptance (temporary precise). |
| **Explicit consent at each stage** | Registration form explains what location data is collected and why. GPS permission prompt at acceptance is browser-native and requires active user action. |
| **No persistent precise GPS in database** | Precise coordinates are held in a Redis key with a TTL of 30 minutes maximum. The key is explicitly deleted on request completion. |
| **Audit log** | Every location data access event is logged with timestamp and requesting service. |
| **Right to deletion** | Donor account deletion triggers immediate purge of all location data (city, state, centroid). |
| **Data minimisation** | Only the minimum data needed for the matching function is collected. No geofencing, no movement history, no background location. |

### Compliance Alignment

| Regulation | Requirement | Compliance |
|---|---|---|
| **DPDP Act (India, 2023)** | Purpose limitation — data collected only for stated purpose | ✅ Location used only for matching and routing |
| **DPDP Act (India, 2023)** | Data minimisation — collect minimum necessary | ✅ City-centroid only; precise GPS transient |
| **DPDP Act (India, 2023)** | Right to erasure | ✅ Account deletion triggers location purge |
| **WHO Ethics Guidelines** | Donor data confidentiality | ✅ No location data shared with third parties |

### Future Scalability

When LifeLink AI grows beyond city-level deployment:
- City-centroid precision can be increased to district or zone level without changing the data model
- Precise GPS can be used for in-app routing guidance in a future mobile app, using the same temporary-only model
- The Redis TTL can be adjusted per deployment context (shorter for high-trust environments)

### Consequences

- **Positive:** Strong privacy posture. Donor trust increased. Regulatory risk reduced. Simpler data model.
- **Negative:** Matching proximity is approximate. Donors in the same city but far apart may be ranked equally. Acceptable at MVP scale.
- **Accepted:** The precision trade-off is acceptable for MVP. Routing accuracy improves post-acceptance when precise GPS is temporarily collected.

---

## 52. ADR-003: Blood Group Data Model

> **ADR ID:** ADR-003
> **Status:** ACCEPTED
> **Deciders:** Chief Software Architect, Principal Engineer
> **Date:** 2026-08-05
> **Resolves:** Section 47 Blocker — Blood Type Data Model

### Context and Problem Statement

The blood group must be stored in the database for every donor record, every blood bank inventory entry, and every emergency request. The decision of how to store this data affects:

- Medical accuracy and safety
- Query performance and indexing
- AI matching engine implementation
- Future scalability to extended antigen systems
- Data integrity and error prevention

The naive approach — storing blood type as a free-text string (e.g., "O Positive", "A Neg", "b+") — introduces format inconsistency, case sensitivity errors, and makes compatibility logic impossible to enforce reliably.

### Decision

Store blood group as **two separate fields**: an ABO enum and an Rh boolean.

### Data Model

| Field | Type | Values | Rationale |
|---|---|---|---|
| `abo_group` | PostgreSQL ENUM | `A`, `B`, `AB`, `O` | Four medically defined ABO groups. Enum prevents invalid entries. |
| `rh_positive` | BOOLEAN | `true` (positive), `false` (negative) | Rh is binary. Boolean is the most natural and efficient representation. |

### Database Representation vs Display Representation

| Stored in Database | Displayed to Users | API Response |
|---|---|---|
| `abo_group = 'O', rh_positive = false` | "O−" | `{ "abo_group": "O", "rh_positive": false, "display": "O-" }` |
| `abo_group = 'A', rh_positive = true` | "A+" | `{ "abo_group": "A", "rh_positive": true, "display": "A+" }` |
| `abo_group = 'AB', rh_positive = true` | "AB+" | `{ "abo_group": "AB", "rh_positive": true, "display": "AB+" }` |
| `abo_group = 'B', rh_positive = false` | "B−" | `{ "abo_group": "B", "rh_positive": false, "display": "B-" }` |

The display string (`"A+"`, `"O-"`) is **computed by the API response serializer**, not stored in the database.

### Compatibility Logic

With this model, the ABO/Rh compatibility matrix becomes a deterministic lookup that can be expressed as a pure boolean function:

```mermaid
flowchart TD
    REQ["Patient Request:\nabo_group=B, rh_positive=true"]
    FILTER_ABO["ABO Filter:\nCompatible donors: B, O\n(A and AB donors excluded)"]
    FILTER_RH["Rh Filter:\nrh_positive=true → can receive any Rh\nrh_positive=false → can only receive rh_positive=false"]
    RESULT["Compatible donors:\nB+ (exact), B- (Rh-safe),\nO+ (ABO-safe), O- (universal)"]

    REQ --> FILTER_ABO --> FILTER_RH --> RESULT
```

**Compatibility rules implemented as boolean logic:**

| Rule | Logic |
|---|---|
| ABO compatibility | Recipient with group X can receive from: X, and O (universal donor). AB can receive from all. |
| Rh compatibility | Rh-positive recipient can receive Rh+ or Rh-. Rh-negative recipient can only receive Rh-. |
| Combined | Compatible = `abo_compatible(donor.abo_group, patient.abo_group) AND rh_compatible(donor.rh_positive, patient.rh_positive)` |

### Why This Model is Correct

| Reason | Explanation |
|---|---|
| **Medically accurate** | ABO and Rh are independent biological systems. Storing them separately reflects their independence and allows each to be evaluated independently. |
| **No invalid states** | PostgreSQL ENUM prevents any value other than A, B, AB, or O. BOOLEAN prevents anything other than true/false. Free-text strings allow "o-", "O negative", "oNeg", etc. |
| **AI matching simplicity** | The compatibility filter in the matching engine becomes a two-field boolean check, not a string comparison or lookup table against 8 possible string formats. |
| **Indexable** | PostgreSQL can create a composite index on `(abo_group, rh_positive)`. This makes inventory queries like "find all O- units" extremely fast, as the index is compact and selective. |
| **Future-proof** | Extended antigen systems (Kell, Duffy, Kidd) can be added as additional boolean columns or a separate `extended_antigens` JSONB field without altering the base model. |

### Consequences

- **Positive:** Data integrity guaranteed by the database. Compatibility logic is simple, testable, and fast. API consumers receive a human-readable `display` field without storing redundant data.
- **Negative:** The display string must be generated by the serializer. This is a minor implementation detail, not a complexity.
- **Accepted:** All downstream systems (matching engine, inventory queries, emergency requests) use the two-field model.

---

## 53. ADR-004: AI Matching Engine Strategy

> **ADR ID:** ADR-004
> **Status:** ACCEPTED
> **Deciders:** Chief Software Architect, Principal Engineer
> **Date:** 2026-08-05
> **Resolves:** Blocker 4 — AI Matching Strategy

### Context and Problem Statement

The product is named "LifeLink AI" and its core value proposition is AI-powered blood donor matching. However, machine learning models — particularly ranking models like Learning to Rank or gradient boosting — require historical training data. At MVP, no such data exists. Training an ML model on zero real emergency outcomes would produce an untrained or randomly initialized model that cannot be relied upon for patient safety decisions.

The question is: **What matching strategy is appropriate for MVP, and how do we evolve toward genuine ML?**

### Decision

### Decision

Use a **hybrid deterministic-medical + advisory AI architecture**:
1. **Deterministic Biological Gate**: Pure Python standard library (`backend/app/core/medical.py`) performs hard ABO/Rh filtering. Incompatible donors or facilities are never scored or presented.
2. **Dual-Supply Candidate Discovery**: Simultaneously discovers matching inventory units from verified Blood Banks and eligible Voluntary Donors.
3. **Multi-Tier Search Radii**: 15 km (Local), 25 km (District), 50 km (Regional default), and 100 km (Intercity).
4. **Advisory AI Propensity Scoring**: Internal FastAPI microservice (`port 8001`) serving `donor-response-v1` (LogisticRegression trained on UCI dataset, ROC-AUC 0.7521, Recall 0.7528) to advise on donor responsiveness $[0.0, 1.0]$.
5. **Deterministic Fallback**: If AI service fails or times out (>5.0s), backend transparently falls back to operational rule scoring (`model_version: deterministic-fallback`).

### Implemented Matching Formulation

```mermaid
flowchart TD
    REQ["Emergency Request\n(Blood Type, Urgency, Coordinates)"]
    GATE["Deterministic Biological Filter\n(backend/app/core/medical.py)"]
    
    subgraph "Candidate Discovery (Radii: 15, 25, 50, 100 km)"
        BB["Blood Banks\n(Unexpired Stock > 0)"]
        DONOR["Voluntary Donors\n(Active, Eligible, Cooldown ≥ 56d)"]
    end
    
    subgraph "Scoring Engines"
        BB_SCORE["Blood Bank Score:\n(Compat × 0.40) + (Stock × 0.35) + (Prox × 0.25)"]
        AI_SVC["AI Service (port 8001):\ndonor-response-v1 Propensity"]
        DONOR_SCORE["Donor Score:\n(Compat × 0.40) + (Prox × 0.30) + (Avail × 0.20) + (AI × 0.10)"]
        FALLBACK["Fallback Score (if AI down):\n(Compat × 0.40) + (Prox × 0.35) + (Avail × 0.25)"]
    end

    PERSIST["Persist MatchRun & MatchCandidates\n(Zero-PII Masking: Donor #DONOR-XXXX)"]
    UI["Render Hospital Matching Workspace UI"]

    REQ --> GATE
    GATE --> BB & DONOR
    BB --> BB_SCORE
    DONOR --> AI_SVC
    AI_SVC -->|"Success"| DONOR_SCORE
    AI_SVC -.->|"Timeout / Error"| FALLBACK
    BB_SCORE & DONOR_SCORE & FALLBACK --> PERSIST --> UI
```

### Approved Scoring Weights

#### 1. Voluntary Donor Candidates
| Factor | Weight | Formulation & Rationale |
|---|:---:|---|
| **Blood Compatibility** | **40%** | Exact ABO/Rh match = 1.0; compatible universal donor = 0.8 |
| **Proximity** | **30%** | $\max(0, 1.0 - \frac{\text{Distance}}{R})$ where $R \in \{15, 25, 50, 100\}\text{ km}$ |
| **Availability** | **20%** | Active status = 1.0; verified profile |
| **AI Response Propensity** | **10%** | Model output $[0.0, 1.0]$ from `donor-response-v1` (advisory behavioral weight) |
| **Total** | **100%** | |

#### 2. Blood Bank Inventory Candidates
| Factor | Weight | Formulation & Rationale |
|---|:---:|---|
| **Blood Compatibility** | **40%** | Exact ABO/Rh match = 1.0; compatible match = 0.8 |
| **Stock Adequacy** | **35%** | $\min(1.0, \frac{\text{Net Available Units}}{\text{Requested Units}})$ |
| **Proximity** | **25%** | $\max(0, 1.0 - \frac{\text{Distance}}{R})$ |
| **Total** | **100%** | |


### Data Collection During MVP (Foundation for ML)

Every interaction logged for future ML training:

| Event | Data Captured |
|---|---|
| Match generated | Donor ID, blood type, distance, availability status, donation history, request urgency, timestamp |
| Notification sent | Donor ID, request ID, notification time |
| Donor accepts | Donor ID, response latency (seconds from notification) |
| Donor declines | Donor ID, decline reason (if provided) |
| Request fulfilled | Time-to-match, total donors notified before acceptance |
| Request cancelled | Reason, stage at cancellation |

### ML Migration Path

```mermaid
gantt
    title AI Matching Engine Evolution
    dateFormat YYYY-MM
    section MVP
        Deterministic Rule Engine    :mvp, 2026-08, 1M
        Data Collection Begins       :data, 2026-08, 6M
    section v1.0
        Learning to Rank (LambdaMART):v1, 2026-11, 3M
        A/B Test vs Rule Engine      :ab, 2027-01, 2M
    section v2.0
        Gradient Boosting (XGBoost)  :v2, 2027-03, 3M
        Donor Churn Prediction       :churn, 2027-04, 2M
    section v3.0
        Neural Ranking               :nr, 2027-09, 3M
        Reinforcement Learning (experimental):rl, 2027-12, 3M
```

| Version | Algorithm | Prerequisite | Expected Improvement |
|---|---|---|---|
| **MVP** | Weighted rule engine (40/30/20/10) | None | Baseline TTM reduction |
| **v1.0** | Learning to Rank (LambdaMART) | 6+ months of real match outcome data | Better donor ordering; fewer no-shows |
| **v2.0** | Gradient Boosting (XGBoost) | 1+ year of data; feature engineering | Demand forecasting; churn prediction |
| **v3.0** | Neural Ranking | 2+ years of data; GPU infrastructure | Sub-minute TTM at national scale |
| **Enterprise** | Reinforcement Learning | Continuous feedback loop; real-time signals | Adaptive real-time matching |

### Consequences

- **Positive:** Safe, explainable, testable, immediately deployable. Generates training data for future ML.
- **Negative:** Rule engine does not learn or adapt. Weights require manual retuning based on pilot feedback.
- **Accepted:** The deterministic engine is the correct choice for MVP. The ML migration path is defined and begins immediately with data collection.

---

## 54. Architecture Freeze Declaration

> **Issued by:** Chief Software Architect
> **Date:** 2026-08-05
> **Effective from:** Version 3.0 of this document

### Declaration

**Phase 1 of the LifeLink AI Master Architecture Blueprint is hereby FROZEN.**

This means:

1. **All product decisions documented in Phase 1 are final.** The Executive Summary, Vision, Mission, Business Problem, Stakeholder Analysis, User Personas, Functional Requirements, Non-Functional Requirements, Business Goals, KPIs, MVP Definition, MVP Acceptance Criteria, Product Scope, Out of Scope, Product Principles, and Product Non-Goals are locked for implementation.

2. **No product-level changes may be made to Phase 1 without a formal ADR.** Any change — however small — to a Functional Requirement, a Non-Functional Requirement, an MVP feature, a KPI target, or a product principle requires:
   - A new Architecture Decision Record (ADR) with ID, status, deciders, date, context, decision, and consequences
   - Review and approval by both team members
   - An update to the ADR log in this section
   - A version bump to this document

3. **Technical implementation documents may evolve freely.** Phase 2 (Technical Blueprint), Phase 3 (Engineering Blueprint), and Phase 4 (Implementation Blueprint) may be updated as technical decisions are made. These phases implement the frozen Phase 1 requirements — they do not change them.

4. **Open Questions in Section 44 are implementation-phase decisions.** OQ1, OQ2, OQ3, OQ5, OQ7, OQ8, OQ9, OQ10 remain open and must be resolved before or during the relevant development module. They do not block the freeze.

### What the Freeze Covers

| Area | Frozen? | Notes |
|---|---|---|
| Executive Summary | ✅ Yes | The business problem and solution are confirmed |
| Vision and Mission | ✅ Yes | North star is set |
| Business Problem | ✅ Yes | Validated against industry data |
| Product Non-Goals | ✅ Yes | Boundaries are declared |
| Functional Requirements | ✅ Yes | All FRs are implementation-ready |
| Non-Functional Requirements | ✅ Yes | Performance, security, reliability targets confirmed |
| MVP Definition | ✅ Yes | 7 modules, P0/P1/P2 classification confirmed |
| MVP Acceptance Criteria | ✅ Yes | Pass/fail criteria per module confirmed |
| KPIs and North Star | ✅ Yes | TTM is confirmed North Star Metric |
| Architecture Decision Records | ✅ Yes | ADR-001 through ADR-004 accepted and binding |
| Technical implementation details | ❌ No | Phase 2 decisions evolve as architecture is designed |
| Sprint planning and task assignments | ❌ No | Phase 4 items |

### ADR Log

| ADR ID | Title | Status | Date | Resolves |
|---|---|---|---|---|
| ADR-001 | Blood Inventory Concurrency Strategy | ✅ Accepted | 2026-08-05 | OQ4 — Race condition on concurrent inventory requests |
| ADR-002 | Donor Location Privacy Strategy | ✅ Accepted | 2026-08-05 | OQ6 — GPS vs city-level location privacy |
| ADR-003 | Blood Group Data Model | ✅ Accepted | 2026-08-05 | Blood type enum/boolean schema decision |
| ADR-004 | AI Matching Engine Strategy | ✅ Accepted | 2026-08-05 | ML vs rule engine at MVP |

---

## 55. Phase 2 Readiness Checklist

> **Purpose:** This checklist confirms that Phase 1 is complete and all pre-conditions for Phase 2 (Technical Blueprint) are satisfied. Phase 2 work must not begin until every item below is checked.

### Product Readiness

- [x] Product Scope Finalized (Section 18 — In Scope / Out of Scope defined)
- [x] MVP Definition Finalized (Section 20 — P0/P1/P2 features locked)
- [x] MVP Acceptance Criteria Defined (Section 20A — Pass/fail criteria per module)
- [x] Product Non-Goals Declared (Section 4A — 12 explicit non-goals)
- [x] Academic Scope vs Product Vision Separated (Section 2A — evaluator boundary set)
- [x] User Roles Finalized (9 roles confirmed in FR-01)
- [x] Functional Requirements Locked (Sections 12: FR-01 through FR-07)
- [x] Non-Functional Requirements Locked (Section 13: NFR-01 through NFR-06)
- [x] KPIs Locked (Section 16 — 10 KPIs with definitions and targets)
- [x] North Star Metric Confirmed (Section 17 — Median Time-to-Match)

### Architecture Decision Records

- [x] ADR-001 Complete — Blood Inventory Concurrency Strategy (PostgreSQL row-level locking confirmed)
- [x] ADR-002 Complete — Donor Location Privacy Strategy (city-level permanent + temporary GPS post-acceptance)
- [x] ADR-003 Complete — Blood Group Data Model (ABO enum + Rh boolean confirmed)
- [x] ADR-004 Complete — AI Matching Engine Strategy (deterministic rule engine at MVP; ML migration path defined)

### Pre-Phase 2 Decisions Required

- [ ] Module Ownership Assigned — Dev 1 and Dev 2 module table signed off
- [ ] Database Schema Designed — Phase 2 DATABASE.md created and reviewed
- [ ] API Contract Designed — Emergency match response schema agreed
- [ ] Emergency Priority Logic Written — CRITICAL/HIGH/MEDIUM/LOW rules signed off
- [ ] Cooling Period Implementation Method Confirmed — Service-layer check via `last_donation_date + 56 days`
- [ ] Tech Stack Versions Locked — `pyproject.toml` and `package.json` pinned
- [ ] Deployment Server Provisioned — VPS ordered, Docker installed
- [ ] Firebase Project Created — FCM keys generated and stored securely
- [ ] Demo Dataset Designed — 20+ donors, 5+ hospitals, 5+ blood banks covering all 8 blood types

### Phase 2 Work Streams Ready to Begin

- [x] Backend Architecture Ready — Modular monolith, FastAPI, PostgreSQL, Redis confirmed (ADR-001, ADR-003, ADR-004)
- [x] Database Design Ready — Blood group model confirmed (ADR-003); concurrency model confirmed (ADR-001)
- [x] AI Architecture Ready — Rule engine weights confirmed (ADR-004); ML migration path defined
- [x] Privacy Architecture Ready — Donor location model confirmed (ADR-002)
- [ ] API Design Ready — Requires Phase 2 API.md to be drafted
- [ ] Frontend Architecture Ready — Requires Phase 2 component structure decision

---

*Phase 1 — Product Blueprint: Version 3.0 — FROZEN*

*This document is the definitive and frozen product blueprint for LifeLink AI.*
*Phase 1 is complete. Phase 2 may now begin.*
*All architectural decisions in Phase 2 and beyond must be traceable to requirements defined in this Phase 1 document.*
*Any change to Phase 1 content after this point requires a formal Architecture Decision Record.*

---

# Phase 2 — Technical Blueprint

---

## 11. System Overview

LifeLink AI is structured as a **Modular Monolith** — a single deployable backend application with clearly separated, independently maintainable modules that can later be extracted into microservices.

The system has three distinct runtime processes:
1. **Next.js Frontend** — serves the web UI.
2. **FastAPI Backend** — handles all business logic and API routing.
3. **FastAPI AI Service** — a separate process for ML inference (runs on port 8001, internal only).

All three are orchestrated via Docker Compose and proxied through Nginx.

---

## 12. High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Browser["Web Browser"]
    end

    subgraph "Presentation Layer"
        NextJS["Next.js Frontend (React + Tailwind)"]
    end

    subgraph "API Gateway"
        APIGW["FastAPI Router (Rate Limiting + Auth Middleware)"]
    end

    subgraph "Application Layer"
        Auth["Auth Module"]
        Donor["Donor Module"]
        Hospital["Hospital Module"]
        BloodBank["Blood Bank Module"]
        Inventory["Inventory Module"]
        Emergency["Emergency Module"]
        Notification["Notification Module"]
        Analytics["Analytics Module"]
        Admin["Admin Module"]
    end

    subgraph "AI Service Layer"
        AIGateway["AI Gateway Module"]
        Matching["Matching Engine (Scikit-learn)"]
        Prediction["Demand Predictor (XGBoost)"]
        OCR["Medical OCR (EasyOCR)"]
        NLP["NLP Processor (spaCy)"]
    end

    subgraph "Data Layer"
        PostgreSQL[("PostgreSQL — Primary Database")]
        Redis[("Redis — Cache and Sessions")]
    end

    subgraph "External Services"
        Firebase["Firebase (Push Notifications)"]
        SMTP["SMTP (Email)"]
        Maps["OpenStreetMap / Nominatim"]
    end

    Browser --> NextJS
    NextJS --> APIGW
    APIGW --> Auth & Donor & Hospital & BloodBank & Inventory & Emergency & Notification & Analytics & Admin
    Emergency --> AIGateway
    AIGateway --> Matching & Prediction & OCR & NLP
    Auth & Donor & Hospital & BloodBank & Inventory & Emergency & Analytics & Admin --> PostgreSQL
    Auth --> Redis
    Emergency --> Redis
    Notification --> Firebase & SMTP
    Emergency & Donor --> Maps
```

---

## 13. Low-Level Architecture

### Request Lifecycle

```mermaid
sequenceDiagram
    participant Client as "Browser / Client"
    participant Middleware as "Auth Middleware"
    participant Router as "FastAPI Router"
    participant Service as "Business Service"
    participant Repository as "Repository Layer"
    participant Cache as "Redis Cache"
    participant DB as "PostgreSQL"

    Client->>Router: HTTP Request + Bearer Token
    Router->>Middleware: Validate JWT
    Middleware->>Cache: Check token blacklist
    Cache-->>Middleware: Not blacklisted
    Middleware->>Middleware: Decode and validate claims
    Middleware-->>Router: User context injected
    Router->>Service: Call service method
    Service->>Cache: Check cache for GET requests
    alt Cache Hit
        Cache-->>Service: Return cached data
    else Cache Miss
        Service->>Repository: Query data
        Repository->>DB: SQL query
        DB-->>Repository: Result set
        Repository-->>Service: Domain objects
        Service->>Cache: Store in cache with TTL
    end
    Service-->>Router: Response object
    Router-->>Client: JSON Response
```

### Backend Module Internal Structure

Each backend module follows this internal layered pattern:

```
module/
├── router.py          # FastAPI route definitions only — no business logic
├── service.py         # Business logic layer — orchestration and rules
├── repository.py      # Database queries via SQLAlchemy — no logic
├── models.py          # SQLAlchemy ORM models
├── schemas.py         # Pydantic request and response schemas
├── exceptions.py      # Module-specific custom exceptions
└── tests/
    ├── test_router.py
    ├── test_service.py
    └── test_repository.py
```

**Strict Rule:** No module may directly import another module's `repository.py`. Cross-module data access must go through that module's `service.py`.

---

## 14. Monolith vs Microservices Decision

### ADR-001: Modular Monolith Architecture

**Decision:** Build a Modular Monolith, not Microservices.

| Criterion | Modular Monolith | Microservices |
|---|---|---|
| Team size | Optimal for 2 developers | Requires 5+ developers |
| Deployment complexity | Simple: one Docker container | High: multiple services and orchestration |
| Development speed | Fast: no network calls between modules | Slow: inter-service communication overhead |
| Debugging | Simple: single process, single log | Hard: distributed tracing required |
| Database management | Single PostgreSQL instance | Separate DB per service — high complexity |
| Testing | Simple end-to-end tests | Complex: service mocking required |
| Future migration path | Can be extracted to microservices later | Already the end state |
| Infrastructure cost | Single VPS | Multiple VMs or Kubernetes cluster |

**Justification:**
The project has 2 developers and 1 month. The overhead of microservices would consume 40–60% of the available development time on infrastructure rather than features. A well-structured modular monolith with clean module boundaries can be decomposed into microservices later if the project scales.

**The AI service is the only exception** — it runs as a separate process because:
1. It uses different Python dependencies (ML libraries) that may conflict.
2. It can be scaled independently if GPU compute is added.
3. It has a clearly defined API boundary.

---

## 15. Frontend Architecture

### Technology: Next.js 14 with App Router, React, Tailwind CSS, TypeScript

**Why Next.js?**
- Server-Side Rendering improves SEO for public pages.
- App Router provides clean file-system-based routing.
- Strong TypeScript support.
- React Query integrates cleanly for server state management.

### Frontend Module Structure

```
frontend/
├── app/
│   ├── (public)/
│   │   ├── page.tsx              # Landing page
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx            # Dashboard shell with sidebar
│   │   ├── patient/
│   │   │   ├── emergency/page.tsx
│   │   │   └── history/page.tsx
│   │   ├── donor/
│   │   │   ├── profile/page.tsx
│   │   │   └── availability/page.tsx
│   │   ├── hospital/
│   │   │   ├── inventory/page.tsx
│   │   │   └── requests/page.tsx
│   │   ├── blood-bank/
│   │   │   ├── stock/page.tsx
│   │   │   └── donations/page.tsx
│   │   └── admin/
│   │       ├── users/page.tsx
│   │       └── analytics/page.tsx
├── components/
│   ├── ui/                       # Reusable primitive components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Modal.tsx
│   │   ├── Badge.tsx
│   │   └── Card.tsx
│   ├── layout/
│   │   ├── Navbar.tsx
│   │   ├── Sidebar.tsx
│   │   └── Footer.tsx
│   └── features/
│       ├── emergency/
│       ├── donor/
│       ├── inventory/
│       └── maps/
├── lib/
│   ├── api.ts                    # Axios instance with interceptors
│   ├── auth.ts                   # Auth helper functions
│   └── utils.ts
├── hooks/
│   ├── useAuth.ts
│   ├── useEmergency.ts
│   └── useInventory.ts
├── store/                        # Zustand global state
│   ├── authStore.ts
│   └── emergencyStore.ts
├── types/
│   └── index.ts                  # Global TypeScript types
└── public/
    └── assets/
```

### State Management
- **Zustand** for global state (auth session, emergency status).
- **React Query (TanStack Query)** for server state management, caching, and background sync.
- **Local component state** for UI-only state such as form inputs and modals.

### Frontend Architecture Principles
1. Pages are thin — they only compose components.
2. Business logic lives in custom hooks.
3. API calls are centralized in `lib/api.ts`.
4. Types are shared across the entire frontend from `types/index.ts`.
5. No direct localStorage access outside `lib/auth.ts`.
6. No business logic in components — only rendering and events.

---

## 16. Backend Architecture

### Technology: FastAPI, Python 3.11, SQLAlchemy 2.x, Alembic, asyncpg

### Application Layering

```mermaid
graph TD
    Router["FastAPI Router Layer (HTTP endpoints, input validation only)"]
    Service["Service Layer (Business logic and orchestration)"]
    Repository["Repository Layer (Database queries only)"]
    Models["ORM Models (SQLAlchemy)"]
    DB[("PostgreSQL")]

    Router --> Service
    Service --> Repository
    Repository --> Models
    Models --> DB
```

### Backend Module Ownership

| Module | Owner | Responsibilities |
|---|---|---|
| auth | Developer 1 | Registration, login, JWT, roles, password reset |
| donor | Developer 1 | Donor profiles, availability, health records |
| hospital | Developer 2 | Hospital registration, staff, inventory requests |
| blood_bank | Developer 2 | Blood bank registration, stock management |
| inventory | Developer 2 | Real-time blood stock, thresholds, alerts |
| emergency | Developer 1 | Emergency requests, status tracking, priority queue |
| notification | Developer 1 | Push, email, in-app notification dispatch |
| ai_gateway | Developer 2 | Proxy requests to AI service, handle AI responses |
| analytics | Developer 2 | Aggregate stats, dashboard data, reports |
| admin | Developer 1 | User management, system configuration |

### Dependency Rules

```
router.py
    └── imports: service.py (same module only)

service.py
    └── imports: repository.py (same module only)
    └── imports: other_module.service (via interface — with care)
    └── imports: notification.service (to dispatch notifications)
    └── FORBIDDEN: other_module.repository
    └── FORBIDDEN: other_module.models

repository.py
    └── imports: models.py (same module only)
    └── FORBIDDEN: anything outside its own module
```

### Middleware Stack (Request Processing Order)

```
Incoming Request
      |
      v
CORS Middleware
      |
      v
Rate Limiting Middleware (Redis-backed, 100 req/min per IP)
      |
      v
Request Logging Middleware (assigns request_id)
      |
      v
JWT Authentication Middleware
      |
      v
Role Authorization (FastAPI dependency injection)
      |
      v
Route Handler
```

---

## 17. AI & Medical Matching Architecture

### Dedicated AI Microservice Topology (Port 8001)

The AI service runs as an isolated microservice container (`lifelink-ai-service`) on internal port `8001`, reachable only by the FastAPI backend within the private Docker bridge network:

```mermaid
graph TD
    subgraph "Backend Service (Port 8000)"
        HospitalWS["Hospital Matching Workspace"]
        MatchSvc["MatchingService (backend/app/modules/matching/service.py)"]
        MedCore["Medical Compatibility (backend/app/core/medical.py)\n[Pure Python Stdlib — Deterministic Biological Gate]"]
        AIGateway["AiGatewayService (HTTP Client + 5.0s Timeout)"]
    end

    subgraph "Internal AI Service (Port 8001)"
        AIFastAPI["AI FastAPI Service (POST /matching/rank)"]
        ModelPipeline["donor-response-v1 Pipeline\n(StandardScaler + LogisticRegression)"]
        DatasetMeta["Trained on UCI Blood Transfusion Dataset\n(ROC-AUC: 0.7521, Recall: 0.7528)"]
    end

    subgraph "Graceful Degradation"
        Fallback["Deterministic Rule Fallback\n(model_version: 'deterministic-fallback')"]
    end

    HospitalWS --> MatchSvc
    MatchSvc --> MedCore
    MedCore -->|"ABO/Rh Compatible Candidates Only"| MatchSvc
    MatchSvc --> AIGateway
    AIGateway -->|"POST /matching/rank"| AIFastAPI
    AIFastAPI --> ModelPipeline --> DatasetMeta
    AIGateway -.->|"On Timeout / Error"| Fallback
    Fallback --> MatchSvc
```

### Deterministic Biological Authority vs Advisory AI

| Layer | Implementation Location | Technology | Role & Authority |
|---|---|---|---|
| **Medical Compatibility (Authoritative)** | `backend/app/core/medical.py` | Pure Python standard library (Zero external ML dependencies) | **Authoritative & Non-Negotiable**: Enforces exact biological ABO/Rh rules for Whole Blood, RBC, and Plasma. Incompatible donors or inventory are immediately excluded before any candidate scoring. |
| **Donor Response Propensity (Advisory)** | `ai/app/models/donor-response-v1/` | Scikit-learn (`Pipeline[StandardScaler, LogisticRegression]`) | **Advisory Behavioral Weight (10%)**: Predicts the likelihood $[0.0, 1.0]$ that an eligible donor will respond to an emergency requisition based on RFM features. |
| **Pessimistic Fallback (Resilience)** | `backend/app/modules/matching/service.py` | Deterministic operational scoring | **Autonomous Continuity**: Automatically scores candidates using $(0.40 \times \text{Compat}) + (0.35 \times \text{Prox}) + (0.25 \times \text{Avail})$ if the AI container is unavailable. |

### AI Model Specifications (`donor-response-v1`)

- **Training Dataset**: UCI Blood Transfusion Service Center Dataset (Open Access / CC BY 4.0, 748 records).
- **Extracted RFM Features**:
  1. `recency_months`: Months since last blood donation.
  2. `frequency_donations`: Total lifetime donations completed.
  3. `time_months`: Donor tenure (months since initial registration).
  *(Note: `monetary_volume_cc` dropped during training due to exact collinearity: $250 \times \text{frequency}$).*
- **Pipeline Architecture**: `Pipeline([('scaler', StandardScaler()), ('classifier', LogisticRegression(class_weight='balanced', random_state=42))])`.
- **Cross-Validation Results (5-Fold Stratified CV)**:
  - **ROC-AUC**: `0.7521`
  - **Recall**: `0.7528`
  - **PR-AUC**: `0.5028`
  - **Brier Score**: `0.2055`
  - **Accuracy**: `0.6618`

### Zero-PII Privacy Protection

In compliance with the Digital Personal Data Protection (DPDP) Act:
1. Candidate feature vectors sent to the AI service contain only RFM metrics and distance, stripped of all personal identifying information (PII).
2. Ranked candidates returned to the hospital matching workspace are formatted with masked tokens (e.g. `Donor #DONOR-XXXX`).
3. Personal contact details (phone, email, exact address) are never transmitted in candidate ranking responses.


---

## 18. Authentication Architecture

### Technology: JWT (Access + Refresh Tokens) + bcrypt password hashing

```mermaid
sequenceDiagram
    participant Client
    participant AuthService
    participant Redis
    participant DB

    Client->>AuthService: POST /api/v1/auth/login
    AuthService->>DB: Fetch user by email
    DB-->>AuthService: User record
    AuthService->>AuthService: Verify bcrypt hash
    AuthService->>AuthService: Generate Access Token (15 min TTL)
    AuthService->>AuthService: Generate Refresh Token (7 day TTL)
    AuthService->>Redis: Store refresh token hash
    AuthService-->>Client: access_token + refresh_token in HttpOnly cookie

    Note over Client,AuthService: Every API request:
    Client->>AuthService: Request with Bearer access_token
    AuthService->>AuthService: Decode JWT, verify signature
    AuthService->>Redis: Check if token is blacklisted
    Redis-->>AuthService: Not blacklisted
    AuthService-->>Client: Request proceeds

    Note over Client,AuthService: Logout:
    Client->>AuthService: POST /api/v1/auth/logout
    AuthService->>Redis: Blacklist access token until its natural expiry
    AuthService->>Redis: Delete refresh token
    AuthService-->>Client: 200 OK
```

### Token Strategy

| Token | TTL | Storage | Purpose |
|---|---|---|---|
| Access Token | 15 minutes | JavaScript memory | API authentication on each request |
| Refresh Token | 7 days | HttpOnly secure cookie | Silently obtain new access tokens |

### Security Rules
- Refresh tokens are stored as HttpOnly cookies — not accessible by JavaScript.
- Access tokens stored in memory — not in localStorage — to prevent XSS theft.
- All tokens signed with HS256 using a 256-bit secret from environment variables.
- Failed login attempts rate-limited to 5 attempts per 15 minutes per IP via Redis.
- Password changes and role changes require re-authentication.

---

## 19. Notification Architecture

### Notification Types

| Type | Trigger | Channel | Priority |
|---|---|---|---|
| Emergency Alert | New emergency request created | Push + Email | CRITICAL |
| Donor Match | AI matched a compatible donor | Push + Email | HIGH |
| Low Inventory | Stock below configured threshold | Email + In-App | HIGH |
| Request Accepted | Donor accepted emergency request | Push + In-App | MEDIUM |
| Donation Reminder | 8 weeks since last donation | Email | LOW |
| System Alert | Admin or system-level events | In-App | LOW |

### Notification Flow

```mermaid
graph TD
    Trigger["Event Trigger in any Module"]
    NotifService["Notification Service"]

    FirebaseAdapter["Firebase Adapter (Push Notifications)"]
    SMTPAdapter["SMTP Adapter (Email)"]
    InAppAdapter["In-App Notifications (DB-backed polling for MVP)"]

    Trigger --> NotifService
    NotifService --> FirebaseAdapter & SMTPAdapter & InAppAdapter
```

**MVP Note:** Notifications are dispatched synchronously within the same request cycle. A background job queue (Celery + Redis) will be introduced in v2.0 to decouple notification delivery from the main request.

---

## 20. Maps and Location Architecture

### Technology: OpenStreetMap with Nominatim geocoding, Leaflet.js on Frontend

**Why OpenStreetMap over Google Maps for MVP?**
- Zero cost — no API key billing risk.
- Nominatim provides free geocoding for moderate usage volumes.
- Leaflet.js is open-source and capable of all required map features.
- The adapter pattern means switching to Google Maps requires changing only one file.

### Location Data Flow

```mermaid
graph LR
    UserInput["User enters location or enables GPS"]
    Nominatim["Nominatim API (Address to Coordinates)"]
    DB[("PostgreSQL (lat/lon stored as DECIMAL)")]
    Haversine["Haversine Distance Calculation in Python"]
    Results["Results Sorted by Distance"]

    UserInput --> Nominatim
    Nominatim --> DB
    DB --> Haversine
    Haversine --> Results
```

### Location Storage
- Latitude stored as `DECIMAL(10, 8)`, longitude as `DECIMAL(11, 8)`.
- PostGIS extension enabled on PostgreSQL for future geospatial query support.
- Geocoded addresses cached in Redis for 24 hours to reduce Nominatim calls.

---

## 21. Analytics Architecture

### MVP Analytics

| Metric | Description |
|---|---|
| Total Donors | Count of registered donors by blood type |
| Total Requests | Emergency requests submitted over time |
| Response Rate | Percentage of requests fulfilled within 2 hours |
| Inventory Levels | Current stock per hospital and blood bank |
| Donation History | Donations per week and month |
| Geographic Distribution | Donors by city and region |

### Analytics Implementation
- All analytics queries execute on PostgreSQL using aggregation.
- Results cached in Redis with a 5-minute TTL.
- Admin dashboard polls the analytics endpoint every 60 seconds.
- No separate analytics database for MVP — direct PostgreSQL queries with indexes.

### Future Analytics (v2.0+)
- Blood demand forecasting charts.
- Shortage prediction heatmaps by region.
- Donor engagement and retention analytics.
- Emergency response time trend analysis.

---

## 22. Complete Module Breakdown

### Module Responsibility Matrix

| Module | Owns | Does NOT Own |
|---|---|---|
| auth | User accounts, tokens, sessions, roles | Profile data, donor-specific data |
| donor | Donor profiles, health info, availability | Auth tokens, blood inventory |
| hospital | Hospital profiles, staff, request creation | Blood bank data, AI models |
| blood_bank | Blood bank profiles, policies, stock input | Hospital data, donor matching |
| inventory | Blood stock levels, thresholds, expiry tracking | Who donates, who requests |
| emergency | Emergency requests, priority, lifecycle status | Matching algorithm, notifications |
| ai_gateway | AI request routing and response handling | ML models, training code |
| notification | Message dispatch, templates, delivery channels | Business triggers — only reacts to events |
| analytics | Aggregate metrics, reports, dashboards | Raw transactional data |
| admin | System configuration, user management | Module-specific business logic |

### Cross-Module Communication Allowed

| Source Module | Target Module | Reason |
|---|---|---|
| emergency | ai_gateway | Trigger donor matching |
| emergency | notification | Alert matched donors |
| inventory | notification | Trigger low-stock alerts |
| donor | notification | Donation reminders |
| auth | (any module) | User context injected via dependency |

### Cross-Module Communication Forbidden

| Forbidden Pattern | Reason |
|---|---|
| emergency.repository → donor.repository | Breaks module encapsulation |
| hospital.service → donor.repository | Must use donor.service instead |
| Any module → auth.repository | Auth data must go through auth.service |
| Any module importing another module's models.py | Hard coupling of database schemas |

---

## 23. Service Communication

### Internal Communication (Within Backend Monolith)
- **Method:** Direct Python function calls between service layers.
- No HTTP calls between modules within the same process.
- Cross-module access only through the public service interface.

### External Communication (Backend to AI Service)
- **Protocol:** REST over HTTP with JSON payloads.
- **Auth:** Internal API key in request headers — not JWT.
- **Timeout:** 5 seconds for matching, 30 seconds for OCR.
- **Retry:** 2 retries with exponential backoff (1s, 2s).
- **Fallback:** Rule-based ABO compatibility table if AI service is unavailable.

### External Communication (Backend to Frontend)
- **Protocol:** REST over HTTP with JSON.
- **Auth:** Bearer JWT token in the Authorization header.
- **Real-time:** HTTP polling (MVP) — WebSocket in v2.0.

### Standard API Response Envelope

All successful responses:
```json
{
  "success": true,
  "data": {},
  "message": "Operation successful",
  "timestamp": "2026-08-03T11:26:00Z",
  "request_id": "req_abc123"
}
```

All error responses:
```json
{
  "success": false,
  "error": {
    "code": "DONOR_NOT_FOUND",
    "message": "No donor found with the given ID",
    "details": {}
  },
  "timestamp": "2026-08-03T11:26:00Z",
  "request_id": "req_abc123"
}
```

---

## 24. Database Overview

> Full schema is in `DATABASE.md`. This section defines ownership and architectural decisions only.

### Database: PostgreSQL 15

**Why PostgreSQL?**
- ACID compliance — critical for medical data integrity.
- PostGIS extension for future geospatial queries.
- JSONB for flexible AI metadata and audit data.
- Excellent async Python drivers via asyncpg.
- Mature ecosystem: SQLAlchemy, Alembic, pgAdmin.

### Core Table Ownership

| Table | Module Owner | Purpose |
|---|---|---|
| users | auth | All user accounts across all roles |
| user_roles | auth | Role assignments per user |
| donors | donor | Donor-specific profile data |
| organ_donors | donor | Organ pledge and medical data |
| hospitals | hospital | Hospital registration and profile |
| hospital_staff | hospital | Staff members per hospital |
| blood_banks | blood_bank | Blood bank registration and profile |
| blood_inventory | inventory | Real-time stock per facility by blood type |
| inventory_history | inventory | Historical stock changes |
| emergency_requests | emergency | Emergency request records and lifecycle |
| emergency_matches | emergency | AI-generated match results per request |
| donations | donor | Donation history records |
| notifications | notification | Notification records and delivery status |
| analytics_snapshots | analytics | Periodic pre-aggregated metric snapshots |

### Database Standards
1. Every table has `id` (UUID primary key), `created_at`, and `updated_at` timestamps.
2. Soft deletes use a `deleted_at` timestamp column instead of hard DELETE.
3. All user-linked tables reference `users.id` as the foreign key.
4. Migrations are managed exclusively via Alembic — no manual SQL on production.
5. Indexing strategy documented in full in `DATABASE.md`.

---

## 25. Caching Strategy

### Technology: Redis 7

| Cache Use Case | Key Pattern | TTL | Invalidation Trigger |
|---|---|---|---|
| JWT blacklist | blacklist:{token_hash} | Token natural expiry | Auto-expires |
| Refresh tokens | refresh:{user_id} | 7 days | On logout |
| Blood inventory | inventory:{facility_id} | 2 minutes | On stock update event |
| Analytics data | analytics:{metric}:{date} | 5 minutes | Time-based only |
| Donor search results | search:{params_hash} | 30 seconds | Time-based only |
| Rate limiting counters | ratelimit:{ip}:{endpoint} | 15 minutes | Auto-expires |
| Geocoded addresses | geocode:{address_hash} | 24 hours | Time-based only |

### Caching Rules
- Cache is always a hint, never a source of truth.
- Critical medical data (inventory, emergency status) has TTL of 2 minutes or less.
- Cache keys include a version prefix: `v1:inventory:{id}` for easy bulk invalidation.
- Redis is never primary storage — PostgreSQL is always the authoritative source.

---

## 26. Recommended Tech Stack

| Layer | Technology | Version | Justification |
|---|---|---|---|
| Frontend Framework | Next.js | 14.x | SSR, App Router, TypeScript-first |
| UI Library | React | 18.x | Component model, large ecosystem |
| Styling | Tailwind CSS | 3.x | Utility-first, rapid iteration |
| State (Global) | Zustand | Latest | Lightweight, no boilerplate |
| State (Server) | React Query (TanStack) | Latest | Caching, background sync |
| Maps Frontend | Leaflet.js + OpenStreetMap | Latest | Free, open-source, full-featured |
| Backend Framework | FastAPI | 0.111.x | Async, Pydantic validation, auto-docs |
| Python Version | Python | 3.11 | Stable LTS with performance improvements |
| ORM | SQLAlchemy | 2.x | Async support, mature and well-supported |
| DB Migrations | Alembic | Latest | Industry standard for SQLAlchemy |
| Primary Database | PostgreSQL | 15.x | ACID, PostGIS, JSONB support |
| Cache and Sessions | Redis | 7.x | Fast key-value, pub/sub support |
| JWT | python-jose | Latest | JWT encoding and decoding |
| Password Hashing | passlib with bcrypt | Latest | Secure, industry-standard |
| ML Framework | Scikit-learn + XGBoost | Latest stable | Matching and prediction models |
| Deep Learning | PyTorch | 2.x | Future OCR and NLP models |
| NLP | spaCy | 3.x | Named entity recognition, text processing |
| OCR | EasyOCR | Latest | Multi-language medical OCR |
| Push Notifications | Firebase Admin SDK | Latest | Reliable, free tier sufficient for MVP |
| Email | SMTP via Gmail or SendGrid | — | Transactional email delivery |
| Containerization | Docker + Docker Compose | Latest | Consistent environments across machines |
| Geocoding | Nominatim via OpenStreetMap | — | Free geocoding, no API key required |
| HTTP Client | Axios | Latest | Interceptors and TypeScript support |
| Validation Backend | Pydantic | v2.x | Built into FastAPI, fast validation |
| Testing Backend | pytest + httpx | Latest | Async-compatible testing |
| Testing Frontend | Jest + React Testing Library | Latest | Component and hook testing |
| Linting Backend | Ruff + mypy | Latest | Fast Python linting and type checking |
| Linting Frontend | ESLint + Prettier | Latest | TypeScript-aware code quality |

---

## 27. Third-Party Services

| Service | Purpose | Cost Tier | Fallback Strategy |
|---|---|---|---|
| Firebase | Push notifications | Free Spark plan | Email-only fallback mode |
| Gmail SMTP / SendGrid | Transactional email | Free tier | Disable email, use in-app only |
| Nominatim (OpenStreetMap) | Address geocoding | Free (rate limited) | Manual latitude/longitude input |
| Docker Hub | Container image registry | Free | GitHub Container Registry |
| GitHub | Version control and CI | Free | GitLab |

### Adapter Pattern — Third-Party Isolation

All third-party services are accessed only through adapter classes. The rest of the codebase never imports SDK code directly.

```
notification/
└── adapters/
    ├── firebase_adapter.py    # Wraps Firebase Admin SDK
    └── smtp_adapter.py        # Wraps smtplib or SendGrid SDK

maps/
└── adapters/
    ├── nominatim_adapter.py   # Wraps Nominatim HTTP API
    └── google_maps_adapter.py # Future: swap in by replacing this file only
```

---

## 28. Folder Structure

```
LifeLink-AI/
│
├── README.md
├── ARCHITECTURE.md               ← This file — Master Blueprint
├── DATABASE.md                   ← Schema, relationships, indexes
├── API.md                        ← Endpoint contracts, request/response formats
├── CHANGELOG.md                  ← Change history per developer per date
│
├── docker-compose.yml            ← Orchestrates all services
├── .env.example                  ← Environment variable template (no secrets)
├── .gitignore
│
├── backend/                      ← FastAPI Application
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml            ← Ruff and mypy configuration
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/             ← Migration files
│   └── app/
│       ├── main.py               ← FastAPI app entry point, router registration
│       ├── config.py             ← Settings via pydantic-settings
│       ├── database.py           ← SQLAlchemy async engine and session factory
│       ├── dependencies.py       ← Shared FastAPI dependency functions
│       ├── core/
│       │   ├── security.py       ← JWT creation, password hashing
│       │   ├── exceptions.py     ← Global exception handlers
│       │   ├── middleware.py     ← CORS, rate limiting, request logging
│       │   └── constants.py      ← App-wide constants
│       └── modules/
│           ├── auth/
│           │   ├── router.py
│           │   ├── service.py
│           │   ├── repository.py
│           │   ├── models.py
│           │   ├── schemas.py
│           │   └── exceptions.py
│           ├── donor/            ← Same structure as auth
│           ├── hospital/
│           ├── blood_bank/
│           ├── inventory/
│           ├── emergency/
│           ├── notification/
│           │   ├── router.py
│           │   ├── service.py
│           │   ├── repository.py
│           │   ├── models.py
│           │   ├── schemas.py
│           │   └── adapters/
│           │       ├── firebase_adapter.py
│           │       └── smtp_adapter.py
│           ├── ai_gateway/
│           ├── analytics/
│           └── admin/
│
├── frontend/                     ← Next.js Application
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── (public)/
│   │   └── (dashboard)/
│   ├── components/
│   │   ├── ui/
│   │   ├── layout/
│   │   └── features/
│   ├── lib/
│   ├── hooks/
│   ├── store/
│   └── types/
│
├── ai/                           ← AI Inference Service
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py               ← AI FastAPI entry point
│       ├── config.py
│       └── modules/
│           ├── matching/
│           │   ├── router.py
│           │   ├── engine.py     ← Matching algorithm
│           │   ├── schemas.py
│           │   └── compatibility.py  ← ABO compatibility matrix
│           ├── prediction/       ← Future v2.0
│           ├── ocr/              ← Future v2.0
│           └── nlp/              ← Future v2.0
│
├── docker/
│   ├── nginx.conf                ← Reverse proxy configuration
│   └── postgres/
│       └── init.sql              ← DB initialization script
│
└── tests/
    └── e2e/                      ← End-to-end integration tests
```

---

## 29. Deployment Architecture

### MVP: Single VPS with Docker Compose

```mermaid
graph TD
    subgraph "Public Internet"
        User["User Browser"]
    end

    subgraph "VPS or Cloud VM"
        Nginx["Nginx Reverse Proxy (port 80 and 443)"]

        subgraph "Docker Internal Network"
            Frontend["Next.js (port 3000)"]
            Backend["FastAPI Backend (port 8000)"]
            AIService["AI Service (port 8001, internal only)"]
            PostgreSQL[("PostgreSQL (port 5432, internal only)")]
            Redis[("Redis (port 6379, internal only)")]
        end
    end

    subgraph "External Services"
        Firebase["Firebase Cloud Messaging"]
        SMTP["Email SMTP Provider"]
        OSM["Nominatim / OpenStreetMap"]
    end

    User --> Nginx
    Nginx -->|"/api/*"| Backend
    Nginx -->|"/* (all other paths)"| Frontend
    Backend -->|"Internal HTTP"| AIService
    Backend --> PostgreSQL & Redis
    Backend --> Firebase & SMTP & OSM
```

### Docker Compose Service Map

| Service | Image | Internal Port | Exposed |
|---|---|---|---|
| nginx | nginx:alpine | 80, 443 | 80, 443 (public) |
| frontend | node:20-alpine | 3000 | No — proxied through Nginx |
| backend | python:3.11-slim | 8000 | No — proxied through Nginx |
| ai-service | python:3.11-slim | 8001 | No — internal Docker network only |
| postgres | postgres:15-alpine | 5432 | No — internal only |
| redis | redis:7-alpine | 6379 | No — internal only |

### Environment Variables Reference

```bash
# Application
APP_ENV=production
SECRET_KEY=<256-bit-random-string>
ACCESS_TOKEN_TTL=900
REFRESH_TOKEN_TTL=604800

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/lifelink
REDIS_URL=redis://redis:6379/0

# AI Service
AI_SERVICE_URL=http://ai-service:8001
AI_SERVICE_API_KEY=<internal-api-key>

# Firebase
FIREBASE_CREDENTIALS_JSON=<base64-encoded-credentials>

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=<email>
SMTP_PASSWORD=<app-password>

# Maps
NOMINATIM_BASE_URL=https://nominatim.openstreetmap.org
```

### Future Deployment Path (v2.0+)
- Migrate to managed cloud: AWS ECS, Railway, Render, or DigitalOcean App Platform.
- PostgreSQL → AWS RDS or Supabase.
- Redis → Upstash or AWS ElastiCache.
- GitHub Actions for CI/CD: run tests on PR, deploy to VPS on merge to main.
- SSL/TLS via Let's Encrypt with Certbot.

---

# Phase 3 — Engineering Blueprint

---

## 30. Development Standards

### Architecture Rules (Non-Negotiable)

1. Every feature belongs to exactly one module.
2. Every module has a single clearly defined responsibility.
3. No module may directly access another module's repository or models.
4. AI must always communicate through the AI Gateway module via HTTP.
5. Frontend must never communicate directly with the database.
6. Authentication logic must remain entirely within the auth module.
7. Every third-party service must be wrapped in an adapter class.
8. Business logic must never exist in the router layer.
9. All AI models must be swappable without modifying backend modules.
10. All configuration comes from environment variables — no hardcoded secrets or URLs.
11. Everything must run in Docker — "works on my machine" is not accepted.
12. ARCHITECTURE.md must be updated before any structural change is implemented.

### What NOT to Build for MVP

The following are explicitly out of scope. Do not implement them during Month 1:

- Kubernetes or any container orchestration platform.
- Kafka, RabbitMQ, or message queues — use synchronous calls.
- Elasticsearch or any full-text search engine.
- GraphQL — REST only for MVP.
- gRPC.
- WebSockets — use polling.
- Mobile application.
- Blockchain.
- Multi-region deployment.
- CI/CD pipelines — deploy manually for MVP.

### Feature Classification Labels

Every feature in discussion must be labeled before implementation:

| Label | Meaning |
|---|---|
| MVP | Build this month |
| Future v2.0 | Next phase after MVP |
| Future v3.0 | Phase after v2.0 |
| Enterprise | Long-term, requires significant infrastructure |
| Research | Experimental, not on any current roadmap |

---

## 31. Coding Standards

### Python Backend and AI Service

```python
# Every Python file begins with a module path comment
# backend/app/modules/emergency/service.py

# Type hints are mandatory on all public function signatures
async def create_emergency_request(
    request: EmergencyCreateSchema,
    current_user: UserSchema,
    db: AsyncSession,
) -> EmergencyResponseSchema:
    ...

# Docstrings are required for all public service methods
async def find_compatible_donors(
    blood_type: str,
    location: LocationSchema,
    units_required: int,
) -> list[DonorMatchSchema]:
    """
    Find compatible blood donors within 50km of the given location.

    Args:
        blood_type: ABO+Rh blood type string such as O- or AB+
        location: Patient or hospital location coordinates
        units_required: Number of blood units required

    Returns:
        Ranked list of compatible donors with distance and availability score.

    Raises:
        BloodTypeInvalidError: If blood_type is not a valid ABO+Rh string.
    """
    ...
```

**Python Style Rules:**
- PEP 8 compliance enforced by Ruff.
- Line length: 88 characters (Black formatter default).
- Formatter: Black — run automatically before commit.
- Linter: Ruff — zero warnings allowed in CI.
- Type checker: mypy in strict mode.
- No `from module import *` anywhere in the codebase.
- No bare `except:` — always catch specific exception types.
- Constants in UPPER_SNAKE_CASE defined in `core/constants.py`.

### TypeScript Frontend

```typescript
// Type all component props explicitly — no implicit any
interface EmergencyCardProps {
  request: EmergencyRequest;
  onAccept: (id: string) => Promise<void>;
  onDecline: (id: string) => void;
  isLoading?: boolean;
}

// Prefer async/await over .then() chains
const fetchEmergencies = async (): Promise<EmergencyRequest[]> => {
  const response = await api.get<ApiResponse<EmergencyRequest[]>>('/emergency/requests');
  return response.data.data;
};
```

**TypeScript Style Rules:**
- `strict: true` in tsconfig.json — no exceptions.
- No `any` types anywhere — use `unknown` if type is truly unknown.
- All API responses typed with the standard envelope interface.
- Components: PascalCase filenames. Utilities: camelCase filenames.
- All hooks start with `use` prefix.
- ESLint and Prettier enforced — no warnings merged to main.

---

## 32. Naming Conventions

### Database (PostgreSQL)

| Item | Convention | Example |
|---|---|---|
| Tables | snake_case plural | emergency_requests, blood_inventory |
| Columns | snake_case | blood_type, created_at, is_active |
| Primary Keys | id (UUID) | id UUID PRIMARY KEY DEFAULT gen_random_uuid() |
| Foreign Keys | {table_singular}_id | donor_id, hospital_id |
| Indexes | idx_{table}_{column} | idx_donors_blood_type |
| Boolean columns | is_{condition} | is_active, is_available, is_verified |
| Timestamp columns | Standard names | created_at, updated_at, deleted_at |

### Backend (Python)

| Item | Convention | Example |
|---|---|---|
| Files | snake_case | emergency_service.py |
| Classes | PascalCase | EmergencyService, DonorRepository |
| Functions and methods | snake_case | find_compatible_donors() |
| Variables | snake_case | blood_type, matched_donors |
| Constants | UPPER_SNAKE_CASE | MAX_DONORS_PER_MATCH |
| Pydantic schemas | PascalCase with suffix | EmergencyCreateSchema, EmergencyResponseSchema |
| SQLAlchemy models | PascalCase | EmergencyRequest, BloodInventory |
| Custom exceptions | PascalCase with Error suffix | DonorNotFoundError, BloodTypeInvalidError |

### Frontend (TypeScript)

| Item | Convention | Example |
|---|---|---|
| Component files | PascalCase | EmergencyCard.tsx, DonorProfile.tsx |
| Custom hooks | camelCase with use prefix | useEmergencyStatus.ts, useInventory.ts |
| Utility files | camelCase | formatBloodType.ts, validateLocation.ts |
| TypeScript interfaces and types | PascalCase | EmergencyRequest, DonorProfile |
| Constants | UPPER_SNAKE_CASE | API_BASE_URL, MAX_RETRY_COUNT |

### API Endpoints

| Rule | Example |
|---|---|
| All endpoints prefixed with /api/v1/ | /api/v1/donors |
| Kebab-case for multi-word resources | /api/v1/emergency-requests |
| Plural resource names | /api/v1/donors, /api/v1/hospitals |
| Maximum 2 levels of nesting | /api/v1/hospitals/{id}/inventory |
| Actions as POST subpaths | /api/v1/emergency/{id}/accept |
| Query params for filtering | /api/v1/donors?blood_type=O-&city=Mumbai |

---

## 33. Git Branch Strategy

### Branch Model: GitHub Flow

```
main (production-ready at all times)
  |
  |--- feature/auth-jwt-refresh      (Developer 1 working)
  |--- feature/inventory-stock-api   (Developer 2 working)
  |
  Both branches merge to main via Pull Request with peer review
```

**Why GitHub Flow over Gitflow?**
- Simpler for 2 developers.
- No overhead of develop/release branches.
- Every merged PR is potentially deployable.
- Less risk of long-lived divergent branches causing merge conflicts.

### Branch Naming

| Type | Pattern | Example |
|---|---|---|
| Feature | feature/{module}-{description} | feature/auth-jwt-refresh |
| Bug fix | fix/{module}-{description} | fix/inventory-stock-calculation |
| Hotfix | hotfix/{description} | hotfix/emergency-null-pointer |
| Documentation | docs/{filename} | docs/update-api-contracts |

### Commit Message Standard (Conventional Commits)

```
<type>(<scope>): <short imperative description>

Types: feat, fix, docs, refactor, test, chore, style
Scopes: auth, donor, hospital, blood-bank, inventory, emergency, ai, frontend, docker

Examples:
feat(emergency): add AI matching integration on request creation
fix(auth): resolve refresh token not expiring on logout
docs(api): update POST /emergency/requests schema in API.md
test(donor): add unit tests for availability toggle service
chore(docker): add health check to postgres service
```

### Pull Request Rules

1. No direct commits to `main` — all changes via Pull Request.
2. Minimum 1 code review from the other developer before merge.
3. PR description must include: what was changed, how it was tested, and screenshots for UI changes.
4. All pytest tests must pass before creating a PR.
5. CHANGELOG.md must be updated in the same PR as the feature.
6. No PR merges during active emergency debugging or demo preparation.

---

## 34. Versioning Strategy

### Application: Semantic Versioning

```
MAJOR.MINOR.PATCH

MAJOR — Breaking architecture changes (new major phase)
MINOR — New features, backward compatible
PATCH — Bug fixes, no new features
```

| Version | Description |
|---|---|
| 1.0.0 | MVP launch — all core P0 and P1 features working |
| 1.1.0 | OCR feature added |
| 1.2.0 | AI demand forecasting added |
| 2.0.0 | Organ donation module — major new feature set |

### API Versioning

- All endpoints use the `/api/v1/` prefix.
- When breaking changes are required, introduce `/api/v2/` alongside v1.
- v1 endpoints are maintained until v2 is stable and migration is complete.

### Database Migration Versioning

- Alembic generates unique migration IDs automatically.
- Every migration file has a descriptive human-readable message.
- Migrations are never edited after they have been applied to any shared environment.
- Rollback scripts are written for every migration that modifies existing data.

---

## 35. Testing Strategy

### Testing Pyramid

```
           /\
          /  \
         / E2E \       -- Few: 2 to 3 critical full user journeys
        /________\
       /          \
      / Integration \   -- Some: All API endpoints tested
     /______________\
    /                \
   /   Unit Tests     \  -- Many: All service logic and utilities
  /____________________\
```

### Backend Testing

| Layer | Tool | Coverage Target | What to Test |
|---|---|---|---|
| Unit | pytest | 70% minimum | Service methods, utility functions, compatibility logic |
| Integration | pytest + httpx | All endpoints | API contracts, auth, error responses |
| Repository | pytest with test database | Repository methods | Query correctness, constraint validation |

**Testing Rules:**
- Tests use a separate test database — never the development database.
- Test database is reset between test runs using pytest fixtures.
- AI service is mocked in backend tests — not called live.
- Every new service method requires a corresponding unit test.

```python
# Example test structure — tests/test_emergency.py

async def test_create_emergency_request_returns_201(
    client, auth_headers, mock_ai_service
):
    response = await client.post(
        "/api/v1/emergency/requests",
        json={"blood_type": "O-", "units": 2, "hospital_id": "uuid-here"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["data"]["status"] == "PENDING"

async def test_emergency_request_requires_authentication(client):
    response = await client.post("/api/v1/emergency/requests", json={})
    assert response.status_code == 401
```

### Frontend Testing

| Layer | Tool | What to Test |
|---|---|---|
| Component | Jest + React Testing Library | Rendering, user interactions, conditional display |
| Custom Hooks | renderHook from RTL | Hook state, side effects, async behavior |
| End-to-End | Playwright (v2.0 only) | Full user journeys: login to emergency submission |

### AI Service Testing

| Test | What is Verified |
|---|---|
| Compatibility matrix | All 64 combinations of 8 blood types x 8 types |
| Matching engine ranking | Correct score ordering, distance weighting |
| Edge cases | No available donors, all donors declined, blood type mismatch |
| Response schema | Output always matches the Pydantic response schema |

---

## 36. Logging Strategy

### Log Levels

| Level | When to Use | Example |
|---|---|---|
| DEBUG | Detailed flow — development only | Querying donors with blood_type = O- |
| INFO | Normal successful operations | Emergency request req_123 created |
| WARNING | Unexpected but recoverable | AI service responded in 4.2s — exceeds 3s target |
| ERROR | Operation failed, system continues | Email notification failed for user_456 |
| CRITICAL | System-level failure, attention needed | Database connection pool exhausted |

### Structured Log Format (JSON)

```json
{
  "timestamp": "2026-08-03T11:26:00.000Z",
  "level": "INFO",
  "service": "lifelink-backend",
  "module": "emergency",
  "request_id": "req_abc123",
  "user_id": "usr_xyz789",
  "message": "Emergency request created",
  "data": {
    "emergency_id": "emr_001",
    "blood_type": "O-",
    "units_required": 2,
    "priority": "CRITICAL"
  }
}
```

### Logging Rules
1. Every API request logged with: request_id, user_id, method, path, status_code, duration_ms.
2. No PII in logs — no passwords, full tokens, patient medical record numbers, or full names.
3. AI decisions are logged with input parameters and output scores for auditability.
4. Logs written to stdout in Docker — container runtime handles collection.
5. In production, log level is INFO — DEBUG is enabled only via environment variable.

---

## 37. Error Handling Strategy

### HTTP Error Code Reference

| Category | HTTP Code | When Returned |
|---|---|---|
| Validation Error | 422 | Invalid request data (Pydantic schema mismatch) |
| Authentication Error | 401 | Missing, expired, or invalid token |
| Authorization Error | 403 | Valid token but insufficient role |
| Not Found | 404 | Resource does not exist |
| Conflict | 409 | Duplicate registration or unique constraint violation |
| AI Service Unavailable | 503 | AI service is down or timeout exceeded |
| Internal Error | 500 | Unexpected unhandled exception |

### Global Exception Handler (FastAPI)

```python
# backend/app/core/exceptions.py

@app.exception_handler(LifeLinkBaseException)
async def lifelink_exception_handler(
    request: Request, exc: LifeLinkBaseException
) -> JSONResponse:
    logger.error(
        "Application error",
        extra={
            "error_code": exc.error_code,
            "request_id": request.state.request_id,
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request.state.request_id,
        },
    )
```

### AI Service Fallback

When the AI service is unreachable or exceeds the 5-second timeout:
1. Log WARNING with AI service response time and error.
2. Fall back to the rule-based ABO compatibility table.
3. Return results with a response flag: `"ai_assisted": false`.
4. Emergency request is never blocked due to AI unavailability.

---

## 38. Security Architecture

### Security Layer Summary

| Layer | Measure |
|---|---|
| Transport | HTTPS/TLS via Let's Encrypt on production |
| Authentication | JWT with 15-minute access token TTL |
| Authorization | Role-based at route level via FastAPI dependency injection |
| Rate Limiting | Redis-backed: 100 requests per minute per IP |
| Input Validation | Pydantic schemas on all API inputs — automatic 422 on failure |
| SQL Injection | SQLAlchemy ORM with parameterized queries only — no raw SQL |
| XSS | React escapes all rendered output by default |
| CORS | Whitelist frontend domain only — no wildcard in production |
| Secrets | All secrets via environment variables — never committed to Git |
| Password Storage | bcrypt with cost factor 12 |
| Docker Security | Containers run as non-root users |

### Security Rules
1. No secrets in source code, Docker images, or Git history — use environment variables.
2. The `.env` file is in `.gitignore`. Only `.env.example` is committed.
3. PostgreSQL and Redis are never accessible from outside the Docker network.
4. The AI service is never accessible from outside the Docker network.
5. All admin endpoints require `SUPER_ADMIN` role verification.
6. Sensitive operations (password change, role change) require re-authentication.
7. Security review of all auth and emergency endpoints before final deployment.

---

## 39. Performance Optimization

### MVP Performance Targets

| Metric | Target |
|---|---|
| API response time P95 | Less than 500ms |
| AI matching response time | Less than 3 seconds |
| Page First Contentful Paint | Less than 2 seconds |
| Blood inventory read (cached) | Less than 100ms |
| Emergency request creation end-to-end | Less than 1 second |

### Optimization Strategies

| Strategy | Applied To | Implementation |
|---|---|---|
| Redis caching | Inventory reads, analytics, search | TTL from 30 seconds to 5 minutes |
| Database indexing | blood_type, location, status, user_id | Defined in DATABASE.md |
| Async database queries | All DB operations | SQLAlchemy async with asyncpg driver |
| Pagination | All list endpoints | limit and offset, maximum 50 per page |
| Next.js SSR / SSG | Public landing pages | Static generation at build time |
| React Query | Frontend data fetching | Stale-while-revalidate, background refetch |
| Connection pooling | PostgreSQL | SQLAlchemy pool: min 5, max 20 connections |
| AI model preloading | Matching engine | Models loaded once at service startup |

---

## 40. Scalability Plan

### Current MVP (Single VPS)
- Single Docker Compose deployment on one VPS.
- Handles approximately 100 concurrent users and 1,000 requests per minute.
- Sufficient for academic demonstration and early testing.

### v2.0 (Vertical Scaling)
- Upgrade VPS to higher CPU and RAM configuration.
- Enable PostgreSQL connection pooling with PgBouncer.
- Redis Cluster for higher cache throughput.
- Estimated capacity: approximately 1,000 concurrent users.

### v3.0 (Cloud Horizontal Scaling)
- Migrate to managed cloud: AWS, GCP, or DigitalOcean.
- Add load balancer in front of multiple backend containers.
- PostgreSQL read replicas for analytics queries.
- CDN for static frontend assets.
- Estimated capacity: approximately 10,000 concurrent users.

### Future Enterprise (Microservices Extraction)
When team grows and module boundaries are proven:
- AI service is already separate — scale independently with GPU instances.
- Extract notification service — high-volume, event-driven, independently scalable.
- Extract inventory service — real-time, high-read, low-latency requirements.
- Introduce Kafka for event-driven communication between services at this scale.

---

## 41. Backup Strategy

### MVP Backup Plan

| Data | Method | Frequency | Retention |
|---|---|---|---|
| PostgreSQL | pg_dump compressed export | Daily | 7 days of backups |
| Redis | RDB snapshot to disk | Every 6 hours | 3 most recent snapshots |
| AI Models | Git repository tags and Docker image | On every model update | All versions retained |
| Environment files | Manual secure storage outside repo | On any change | Permanent |

### Recovery Procedure
1. Stop all Docker services.
2. Restore PostgreSQL from latest pg_dump backup.
3. Restart all services.
4. Verify `/health` endpoint on backend and AI service.
5. Run smoke tests on critical endpoints.

---

## 42. Monitoring Strategy

### MVP Monitoring (Minimal Overhead)

| Tool | Monitors | Cost |
|---|---|---|
| Docker logs | Application log output | Free |
| PostgreSQL pg_stat_activity | Active connections and slow queries | Free |
| UptimeRobot | External service uptime checks every 5 minutes | Free tier |
| Health endpoint GET /health | Internal dependency status | Free |

### Health Check Endpoint Response

```json
{
  "status": "healthy",
  "service": "lifelink-backend",
  "version": "1.0.0",
  "timestamp": "2026-08-03T11:26:00Z",
  "dependencies": {
    "database": "healthy",
    "redis": "healthy",
    "ai_service": "healthy"
  }
}
```

### Future Monitoring (v2.0+)
- Prometheus metrics endpoint on backend for request latency, error rates, and queue depth.
- Grafana dashboard for real-time visualization.
- Sentry for automatic error capture with stack traces and alerting.
- Structured log aggregation via Loki or AWS CloudWatch.

---

# Phase 4 — Implementation Blueprint

---

## 43. Complete Development Roadmap

```mermaid
gantt
    title LifeLink AI — 1 Month Development Roadmap
    dateFormat  YYYY-MM-DD
    axisFormat  %d-%b

    section Week 1 — Foundation
    Architecture and Documentation      :done, a1, 2026-08-03, 3d
    DATABASE.md and API.md design       :done, a2, after a1, 2d
    Repo setup and Docker Compose       :done, a3, after a1, 2d

    section Week 2 — Core Backend
    Auth Module (Register Login JWT)    :b1, 2026-08-10, 3d
    Donor Module (Profile Availability) :b2, after b1, 2d
    Hospital and Blood Bank Modules     :b3, 2026-08-10, 5d

    section Week 3 — Intelligence Layer
    Inventory Module and Alerts         :c1, 2026-08-17, 3d
    Emergency Module and Priority Queue :c2, after c1, 2d
    AI Matching Engine                  :c3, 2026-08-17, 4d
    Notification System                 :c4, 2026-08-21, 2d

    section Week 4 — Frontend and Integration
    Frontend Auth and Donor UI          :d1, 2026-08-24, 2d
    Frontend Hospital and Inventory UI  :d2, after d1, 2d
    Frontend Emergency and Maps UI      :d3, after d2, 2d
    Full Integration and Bug Fixes      :d4, 2026-08-29, 2d
    Deployment and Demo Preparation     :d5, 2026-09-01, 2d
```

---

## 44. Weekly Milestones

### Week 1 — Architecture and Foundation (Days 1 to 7)

| Day | Task | Owner |
|---|---|---|
| 1 to 3 | Finalize ARCHITECTURE.md, DATABASE.md, API.md | Both |
| 3 to 4 | Initialize GitHub repo, branch strategy, .gitignore | Developer 1 |
| 3 to 4 | Build Docker Compose stack (postgres, redis, nginx) | Developer 2 |
| 5 to 6 | Scaffold FastAPI backend and Next.js frontend | Both |
| 6 to 7 | Run first Alembic migration, verify health endpoint | Both |

**Exit Criteria:** Docker Compose brings up all 5 services. `GET /health` returns 200 on backend. Next.js landing page loads without errors.

---

### Week 2 — Core Backend (Days 8 to 14)

| Day | Task | Owner |
|---|---|---|
| 8 to 10 | Auth Module: register, login, JWT, refresh, logout | Developer 1 |
| 8 to 12 | Hospital Module and Blood Bank Module CRUD | Developer 2 |
| 11 to 12 | Donor Module: profile, health info, availability toggle | Developer 1 |
| 13 to 14 | Unit tests for all Week 2 modules | Both |

**Exit Criteria:** A user can register, login, receive a JWT, create a donor profile, create a hospital, and create a blood bank — all verified via Swagger UI.

---

### Week 3 — Intelligence Layer (Days 15 to 21)

| Day | Task | Owner |
|---|---|---|
| 15 to 17 | Inventory Module: CRUD, low-stock alert thresholds | Developer 2 |
| 15 to 18 | AI Service: blood compatibility matching engine | Developer 2 |
| 18 to 19 | Emergency Module: request creation and priority queue | Developer 1 |
| 19 to 20 | Emergency to AI Gateway integration and fallback | Developer 1 and Developer 2 |
| 20 to 21 | Notification Module: email and push adapters | Developer 1 |

**Exit Criteria:** Submit an emergency request via API → AI matching returns ranked donors → Push notification sent to matched donors.

---

### Week 4 — Frontend and Integration (Days 22 to 30)

| Day | Task | Owner |
|---|---|---|
| 22 to 23 | Frontend: Login, Register, Donor dashboard | Developer 1 |
| 22 to 24 | Frontend: Hospital inventory dashboard | Developer 2 |
| 24 to 25 | Frontend: Emergency request submission and status | Developer 1 |
| 25 to 26 | Frontend: Map view with OpenStreetMap and Leaflet | Developer 2 |
| 26 to 27 | Full end-to-end integration testing | Both |
| 27 to 28 | Bug fixes and edge case handling | Both |
| 29 to 30 | VPS deployment and final demo preparation | Both |

**Exit Criteria:** A patient submits an emergency request via the UI, the system shows matched donors on a map, matched donors receive push notifications, and the request status updates in real time. Full demo flow works end-to-end.

---

## 45. Team Responsibilities

### Developer 1 — Platform Lead

**Module Ownership:**
- auth — Registration, login, JWT, roles, password reset
- donor — Profile, availability, health records, donation history
- emergency — Request submission, priority classification, status lifecycle
- notification — Push, email, in-app dispatch and adapters
- admin — User management and system configuration

**Frontend Ownership:**
- Authentication pages (login, register)
- Donor dashboard (profile, availability, history)
- Patient emergency portal (submit, track)

**Shared:**
- AI Gateway integration (consuming and parsing AI responses)
- Code reviews for Developer 2's pull requests
- CHANGELOG.md updates on every merge

---

### Developer 2 — Infrastructure and AI Lead

**Module Ownership:**
- hospital — Registration, staff management
- blood_bank — Registration, stock input policies
- inventory — Real-time stock, threshold alerts, expiry tracking
- ai_gateway — Routing backend requests to AI service
- analytics — Aggregates, dashboard metrics, reports

**AI Service Ownership:**
- Blood compatibility matching engine
- ABO + Rh compatibility matrix
- AI service Docker setup and dependency management

**Infrastructure Ownership:**
- Docker Compose configuration
- Alembic migration management
- Redis caching layer configuration
- Nginx configuration

**Frontend Ownership:**
- Hospital inventory dashboard
- Blood bank stock management UI
- Map view with Leaflet.js

**Shared:**
- Code reviews for Developer 1's pull requests
- CHANGELOG.md updates on every merge
- Database schema decisions (both must agree before migration)

---

### Daily Sync Protocol

Both developers sync for 15 minutes at the start of each working session:
- What did I complete yesterday?
- What am I working on today?
- What is blocking me?
- Do any API contracts need to change? (Update API.md before coding)
- Do any database tables need to change? (Update DATABASE.md before migration)

---

## 46. Product Backlog

| Epic | Feature | Priority | Owner | Effort | Dependency |
|---|---|---|---|---|---|
| Authentication | User registration | P0 | Dev 1 | 1 day | None |
| Authentication | Login and JWT issuance | P0 | Dev 1 | 1 day | Registration |
| Authentication | JWT refresh token | P0 | Dev 1 | 0.5 day | JWT |
| Authentication | Role-based access control | P0 | Dev 1 | 1 day | JWT |
| Authentication | Password reset via email | P2 | Dev 1 | 1 day | Email |
| Donor | Donor profile creation | P0 | Dev 1 | 1 day | Auth |
| Donor | Availability toggle | P0 | Dev 1 | 0.5 day | Donor profile |
| Donor | Donation history view | P1 | Dev 1 | 0.5 day | Donor profile |
| Donor | Health records and eligibility | P1 | Dev 1 | 1 day | Donor profile |
| Hospital | Hospital registration | P0 | Dev 2 | 1 day | Auth |
| Hospital | Staff management | P1 | Dev 2 | 1 day | Hospital registration |
| Hospital | Inventory view and request | P0 | Dev 2 | 0.5 day | Inventory module |
| Blood Bank | Blood bank registration | P0 | Dev 2 | 1 day | Auth |
| Blood Bank | Stock management CRUD | P0 | Dev 2 | 2 days | Blood bank registration |
| Blood Bank | Low-stock alert thresholds | P1 | Dev 2 | 0.5 day | Stock management |
| Inventory | Real-time stock tracking | P0 | Dev 2 | 2 days | Blood bank |
| Inventory | Inventory update history | P2 | Dev 2 | 0.5 day | Stock tracking |
| Emergency | Submit emergency request | P0 | Dev 1 | 1 day | Auth, Inventory |
| Emergency | Priority classification | P0 | Dev 1 | 0.5 day | Request submission |
| Emergency | Real-time status tracking | P0 | Dev 1 | 1 day | Request submission |
| Emergency | Request history view | P1 | Dev 1 | 0.5 day | Request submission |
| AI Matching | ABO + Rh compatibility matrix | P0 | Dev 2 | 1 day | None |
| AI Matching | Proximity scoring via Haversine | P0 | Dev 2 | 1 day | Donor location data |
| AI Matching | Ranked match output with scores | P0 | Dev 2 | 1 day | Compatibility matrix |
| Notifications | Email dispatch via SMTP | P1 | Dev 1 | 1 day | SMTP configuration |
| Notifications | Push dispatch via Firebase | P1 | Dev 1 | 1 day | Firebase configuration |
| Notifications | In-app notification list | P2 | Dev 1 | 1 day | Frontend |
| Maps | Address geocoding via Nominatim | P1 | Dev 2 | 1 day | Nominatim API |
| Maps | Donor and facility map view | P1 | Dev 2 | 1 day | Geocoding |
| Analytics | Donation count statistics | P2 | Dev 2 | 1 day | Donation records |
| Analytics | Inventory level charts | P2 | Dev 2 | 0.5 day | Inventory module |
| Analytics | Emergency request trends | P2 | Dev 2 | 0.5 day | Emergency records |
| Admin | User management dashboard | P1 | Dev 1 | 1 day | Auth module |
| Admin | System overview and health | P2 | Dev 1 | 1 day | All modules |

---

## 47. Architecture Decision Records

### ADR-001: Modular Monolith

See Section 14 — Monolith vs Microservices Decision.

---

### ADR-002: FastAPI over Django and Flask

**Decision:** FastAPI for the backend.

| Factor | FastAPI | Django REST | Flask |
|---|---|---|---|
| Async support | First-class native | Limited via ASGI | Via extensions only |
| Type safety | Pydantic built-in | Serializers verbose | None |
| Auto documentation | Swagger and ReDoc auto-generated | Manual | Manual |
| Performance | Excellent async performance | Slower sync default | Moderate |
| AI integration | Same Python ecosystem | Same | Same |

**Justification:** FastAPI's built-in Pydantic validation, auto-generated API documentation, and first-class async support are directly aligned with the project's needs. Swagger UI accelerates development by allowing both developers to test endpoints without a frontend.

---

### ADR-003: PostgreSQL over MongoDB and MySQL

**Decision:** PostgreSQL as the primary database.

| Factor | PostgreSQL | MongoDB | MySQL |
|---|---|---|---|
| ACID compliance | Full | Eventual consistency | Full |
| Medical data suitability | Excellent — no data inconsistency risk | Poor for critical records | Good |
| JSON storage | JSONB — fast and indexed | Native JSON | Limited |
| Geospatial | PostGIS extension | GeoJSON support | Limited |
| Async Python driver | asyncpg — excellent | Motor — good | aiomysql — adequate |

**Justification:** Medical data integrity requires strict ACID compliance. MongoDB's eventual consistency model is unacceptable for emergency request and blood inventory records. PostgreSQL's JSONB and PostGIS support provide flexibility for future AI metadata and location features.

---

### ADR-004: JWT Stateless Authentication

**Decision:** JWT over server-side sessions.

**Benefits:**
- Stateless: backend servers do not need to share session state.
- Role claims embedded in token: no database call required per request.
- Standard format: mobile app integration in v2.0 requires no changes.

**Drawbacks and Mitigations:**
- Tokens cannot be invalidated before expiry. Mitigation: 15-minute TTL and Redis blacklist on logout.
- Token payload size is larger than a session cookie. Acceptable at approximately 500 bytes.

---

### ADR-005: REST over GraphQL

**Decision:** REST API for MVP.

**Justification:** GraphQL requires additional schema design, resolver implementation, and frontend integration complexity. REST with well-designed resource URLs and consistent response envelopes is sufficient for the data access patterns in this system. The auto-generated Swagger documentation partially eliminates GraphQL's discoverability advantage. GraphQL can be introduced in v3.0 if flexible client-driven queries become a requirement.

---

### ADR-006: OpenStreetMap over Google Maps

**Decision:** OpenStreetMap with Nominatim and Leaflet.js for MVP.

**Justification:** Google Maps Platform requires billing account setup and carries a risk of unexpected charges during development. Nominatim provides free geocoding at moderate usage volumes. Leaflet.js is fully capable of all required map display features. The adapter pattern ensures that switching to Google Maps in v2.0 requires only a single file change.

---

### ADR-007: Synchronous AI Calls for MVP

**Decision:** AI matching triggered synchronously within the emergency request HTTP cycle.

**Justification:** Emergency requests need a matched donor list in the immediate API response for acceptable UX. AI matching runs in under 3 seconds for MVP data volumes. An asynchronous background queue via Celery and Redis will be introduced in v2.0 when concurrent emergency volume grows and response time optimization becomes necessary.

---

## 48. Risk Analysis

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| AI service unavailable | Medium | High | Rule-based ABO fallback always available |
| Database performance under load | Low | High | Caching and indexing strategy defined upfront |
| Scope creep beyond MVP | High | High | Strict P0/P1/P2 labels; defer P2 if behind schedule |
| Merge conflicts between developers | High | Medium | Clear module ownership; daily sync; short-lived branches |
| Firebase push notification failures | Medium | Medium | Email fallback; retry logic with exponential backoff |
| Nominatim geocoding rate limits | Medium | Low | Cache geocoded addresses for 24 hours in Redis |
| VPS downtime during demo | Low | Critical | Full data backup; alternate hosting option ready |
| AI module complexity overrun | Medium | High | Rule-based matching can substitute entirely if needed |
| Authentication security vulnerability | Low | Critical | Security review before deployment; rate limiting enforced |
| Third-party API key exposed in Git | Low | Critical | Secrets only in .env; .env in .gitignore; scan Git history before push |

---

## 49. Future AI Pipeline

The architecture reserves dedicated integration points for all future AI modules. All new AI capabilities plug into the AI service through new endpoints — no changes to any backend module are required.

```mermaid
graph TD
    AIGateway["AI Gateway Module in Backend"]

    subgraph "MVP — Active"
        M1["Blood Compatibility Matching Engine"]
        M2["Emergency Request Prioritization"]
    end

    subgraph "Future v2.0"
        M3["Demand Forecasting (XGBoost)"]
        M4["Medical Report OCR (EasyOCR)"]
        M5["NLP Emergency Parser (spaCy)"]
    end

    subgraph "Future v3.0"
        M6["Donor Ranking ML (Scikit-learn)"]
        M7["Organ Matching Assistance"]
        M8["Hospital Recommendation Engine"]
        M9["Fraud Detection Model"]
    end

    subgraph "Enterprise Vision"
        M10["LLM Emergency Chat (GPT or Gemini API)"]
        M11["Disease Outbreak Prediction"]
        M12["AI Voice Assistant"]
        M13["Blood Inventory Forecasting"]
    end

    AIGateway --> M1 & M2
    AIGateway -.->|"v2.0"| M3 & M4 & M5
    AIGateway -.->|"v3.0"| M6 & M7 & M8 & M9
    AIGateway -.->|"Enterprise"| M10 & M11 & M12 & M13
```

### AI Expansion Rules
1. Every new AI capability is a new endpoint in the AI service — no backend module changes.
2. Every model is versioned and stored in `ai/models/` with a version suffix.
3. A/B testing of models is supported: the AI Gateway can route requests to `model_v1` or `model_v2` via configuration.
4. Models are trained offline on historical data and deployed as serialized files (`.pkl` or `.pt`).
5. Inference performance metrics (latency, confidence score) are logged for every prediction.

---

## 50. Future Scope and Expansion

### Feature Expansion Roadmap

| Timeline | Feature | Classification |
|---|---|---|
| Month 2 | Medical Report OCR | Future v2.0 |
| Month 2 | AI Demand Forecasting | Future v2.0 |
| Month 2 | NLP Emergency Request Parser | Future v2.0 |
| Month 3 | Mobile Application (React Native) | Future v2.0 |
| Month 3 | Organ Donation Module | Future v2.0 |
| Month 4 | Government Analytics Dashboard | Future v3.0 |
| Month 5 | Blockchain Donation Audit Trail | Future v3.0 |
| Month 6 | National Blood Registry Public API | Future v3.0 |
| Year 2 | Hospital ERP System Integration | Enterprise |
| Year 2 | IoT Blood Storage Monitoring | Enterprise |
| Year 2 | Drone Delivery Coordination | Enterprise |
| Year 2 | AI Voice Assistant for Emergencies | Enterprise |
| Year 2 | Regional Language Support (10+ languages) | Enterprise |
| Year 3 | Real-Time Event Streaming with Kafka | Enterprise |
| Year 3 | Developer SDK and Public API Platform | Enterprise |
| Year 3 | ML Research Platform and Data Pipelines | Enterprise |

### Architecture Reserved Expansion Slots

The current modular architecture reserves forward-compatibility for future growth:

| Future Feature | Reserved Integration Point |
|---|---|
| Mobile App | API-first design means React Native can reuse all API contracts and response types |
| Blockchain | Donation history module can emit events to a blockchain audit adapter with no module changes |
| IoT Storage | Inventory module has a sensor ingestion endpoint slot pre-defined in the schema |
| Offline Mode | AI matching can be packaged as a local inference model for areas without connectivity |
| Multi-tenancy | All facility tables include an organization_id column for future multi-organization support |
| Wearable Devices | Donor health data schema is extensible to accept wearable health metrics |

---

## Architecture Review Checklist

Before any implementation begins, both developers must confirm:

- [ ] No circular dependencies between modules.
- [ ] Every module has a single, clear, documented responsibility.
- [ ] All API contracts documented and agreed upon in API.md.
- [ ] All database tables and relationships documented in DATABASE.md.
- [ ] All environment variables listed in .env.example.
- [ ] Docker Compose starts all services successfully on both machines.
- [ ] Auth module tested and working before any protected endpoint is built.
- [ ] AI service rule-based fallback implemented before AI service is integrated.
- [ ] All third-party services accessed only through adapter classes.
- [ ] .env is in .gitignore and has never been committed.
- [ ] CHANGELOG.md is initialized and up to date.
- [ ] Both developers have read, reviewed, and agreed to this document.

---

*LifeLink AI — Master Architecture Blueprint*
*Version 1.0 — Last Updated 2026-08-03*
*This document is the single source of truth. Update it before changing anything else.*

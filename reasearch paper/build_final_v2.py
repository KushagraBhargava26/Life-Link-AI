"""
build_final_v2.py  —  LifeLink AI IEEE MedAI 2026
Matches the LaTeX source content exactly.
Target: ≤ 12 pages.
"""
import pathlib, re
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, FrameBreak, NextPageTemplate, KeepTogether, Image
)
import pypdf

OUT_DIR   = pathlib.Path(r"d:\A\LifeLink_AI\reasearch paper")
PDF_PATH  = OUT_DIR / "LifeLink_AI_IEEE_MedAI_2026_FINAL.pdf"
FIG1_PATH = OUT_DIR / "latex_project" / "figures" / "lifelink_architecture.png"

# ── Layout ───────────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = letter
MARGIN_T = 0.75 * inch
MARGIN_B = 0.85 * inch
MARGIN_L = 0.75 * inch
MARGIN_R = 0.75 * inch
COL_GAP  = 0.25 * inch
COL_W    = (PAGE_W - MARGIN_L - MARGIN_R - COL_GAP) / 2.0
FULL_W   = PAGE_W - MARGIN_L - MARGIN_R
TITLE_H  = 4.50 * inch   # top frame for title+abstract

# ── Styles ───────────────────────────────────────────────────────────────────
BODY = ParagraphStyle("B",  fontName="Times-Roman",  fontSize=9.8,  leading=13.0,
                      alignment=TA_JUSTIFY, spaceAfter=3.5, firstLineIndent=12)
BNI  = ParagraphStyle("BN", fontName="Times-Roman",  fontSize=9.8,  leading=13.0,
                      alignment=TA_JUSTIFY, spaceAfter=3.5)
ABS  = ParagraphStyle("A",  fontName="Times-Italic", fontSize=8.5,  leading=11.0,
                      alignment=TA_JUSTIFY, spaceAfter=2.5, leftIndent=10, rightIndent=10)
SEC  = ParagraphStyle("S",  fontName="Times-Bold",   fontSize=10.0, leading=13.0,
                      alignment=TA_CENTER, spaceBefore=8.0, spaceAfter=3.5, keepWithNext=True)
SUB  = ParagraphStyle("U",  fontName="Times-Italic", fontSize=9.8,  leading=12.5,
                      alignment=TA_LEFT,   spaceBefore=5.5, spaceAfter=2.5, keepWithNext=True)
TTL  = ParagraphStyle("T",  fontName="Times-Bold",   fontSize=15.0, leading=18.5,
                      alignment=TA_CENTER, spaceAfter=4.0)
AUT  = ParagraphStyle("Au", fontName="Times-Roman",  fontSize=10.0, leading=13.0,
                      alignment=TA_CENTER, spaceAfter=2.0)
AFF  = ParagraphStyle("Af", fontName="Times-Italic", fontSize=9.0,  leading=11.5,
                      alignment=TA_CENTER, spaceAfter=3.0)
TCAP = ParagraphStyle("TC", fontName="Times-Bold",   fontSize=8.2,  leading=10.0,
                      alignment=TA_CENTER, spaceBefore=3.5, spaceAfter=1.5, keepWithNext=True)
FCAP = ParagraphStyle("FC", fontName="Times-Roman",  fontSize=8.2,  leading=10.0,
                      alignment=TA_JUSTIFY, spaceBefore=2.0, spaceAfter=3.5)
TH   = ParagraphStyle("TH", fontName="Times-Bold",   fontSize=7.8,  leading=9.5,  alignment=TA_CENTER)
TC   = ParagraphStyle("Tc", fontName="Times-Roman",  fontSize=7.8,  leading=9.5,  alignment=TA_LEFT)
TCC  = ParagraphStyle("Tcc",fontName="Times-Roman",  fontSize=7.8,  leading=9.5,  alignment=TA_CENTER)
REF  = ParagraphStyle("R",  fontName="Times-Roman",  fontSize=8.0,  leading=10.2,
                      alignment=TA_JUSTIFY, spaceAfter=2.2, leftIndent=12, firstLineIndent=-12)
BUL  = ParagraphStyle("BL", fontName="Times-Roman",  fontSize=9.8,  leading=12.8,
                      alignment=TA_JUSTIFY, spaceAfter=2.5, leftIndent=10, firstLineIndent=-8)
EQT  = ParagraphStyle("EQ", fontName="Times-Italic", fontSize=9.2,  leading=11.5, alignment=TA_CENTER)
EQN  = ParagraphStyle("EN", fontName="Times-Roman",  fontSize=9.0,  leading=11.5, alignment=TA_RIGHT)

def HR(): return HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=2, spaceBefore=1)
def sp(h=3): return Spacer(1, h)
def s(t, i=True): return Paragraph(t, BODY if i else BNI)
def sec(n, t): return Paragraph(f"{n}. {t}", SEC)
def sub(l, t): return Paragraph(f"<i>{l}. {t}</i>", SUB)
def bul(t): return Paragraph(f"&#x2022; {t}", BUL)

def eq(text, num, h=0):
    pe = Paragraph(text, EQT)
    pn = Paragraph(num, EQN)
    t = Table([[pe, pn]], colWidths=[COL_W-0.42*inch, 0.42*inch])
    t.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
        ('TOPPADDING',(0,0),(-1,-1),1.5+h), ('BOTTOMPADDING',(0,0),(-1,-1),1.5+h),
    ]))
    return t

def tbl(data, cw=None, center=None):
    center = center or []
    rows = []
    for ri, row in enumerate(data):
        prow = []
        for ci, cell in enumerate(row):
            if ri == 0: prow.append(Paragraph(str(cell), TH))
            elif ci in center: prow.append(Paragraph(str(cell), TCC))
            else: prow.append(Paragraph(str(cell), TC))
        rows.append(prow)
    cw = cw or [COL_W/len(data[0])]*len(data[0])
    t = Table(rows, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), colors.HexColor("#E0E0E0")),
        ("GRID",(0,0),(-1,-1), 0.3, colors.black),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("TOPPADDING",(0,0),(-1,-1),1.2), ("BOTTOMPADDING",(0,0),(-1,-1),1.2),
        ("LEFTPADDING",(0,0),(-1,-1),2.5), ("RIGHTPADDING",(0,0),(-1,-1),2.5),
    ]))
    return t

# ── Page callbacks ────────────────────────────────────────────────────────────
def pg1(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Bold", 8.2)
    canvas.drawCentredString(PAGE_W/2, PAGE_H-MARGIN_T+9,
        "4th IEEE International Conference on Medical Artificial Intelligence (IEEE MedAI 2026)")
    canvas.setFont("Times-Italic", 7.8)
    canvas.drawCentredString(PAGE_W/2, PAGE_H-MARGIN_T-1,
        "Track: Areas in Medicine & Healthcare Benefited from AI \u2014 Area 3: Digital and Precise Medicine")
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN_L, PAGE_H-MARGIN_T-5, PAGE_W-MARGIN_R, PAGE_H-MARGIN_T-5)
    canvas.setFont("Times-Roman", 7.8)
    canvas.drawCentredString(PAGE_W/2, MARGIN_B-0.28*inch, "Page 1")
    canvas.restoreState()

def pgN(canvas, doc):
    canvas.saveState()
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN_L, PAGE_H-MARGIN_T+4, PAGE_W-MARGIN_R, PAGE_H-MARGIN_T+4)
    canvas.setFont("Times-Italic", 7.8)
    canvas.drawString(MARGIN_L, PAGE_H-MARGIN_T+6, "IEEE MedAI 2026 \u2014 Area 3: Digital and Precise Medicine")
    canvas.drawRightString(PAGE_W-MARGIN_R, PAGE_H-MARGIN_T+6,
        "LifeLink AI: Trustworthy Emergency Blood Matching")
    canvas.setFont("Times-Roman", 7.8)
    canvas.drawCentredString(PAGE_W/2, MARGIN_B-0.28*inch, f"Page {doc.page}")
    canvas.restoreState()

class Doc(BaseDocTemplate):
    def __init__(self, fn, **kw):
        super().__init__(fn, **kw)
        tf = Frame(MARGIN_L, PAGE_H-MARGIN_T-TITLE_H, FULL_W, TITLE_H,
                   id="top", topPadding=0, bottomPadding=0, leftPadding=0, rightPadding=0)
        c1 = Frame(MARGIN_L, MARGIN_B, COL_W,
                   PAGE_H-MARGIN_T-MARGIN_B-TITLE_H-0.04*inch,
                   id="c1l", topPadding=0, bottomPadding=0, leftPadding=0, rightPadding=0)
        c2 = Frame(MARGIN_L+COL_W+COL_GAP, MARGIN_B, COL_W,
                   PAGE_H-MARGIN_T-MARGIN_B-TITLE_H-0.04*inch,
                   id="c1r", topPadding=0, bottomPadding=0, leftPadding=0, rightPadding=0)
        l2 = Frame(MARGIN_L, MARGIN_B, COL_W, PAGE_H-MARGIN_T-MARGIN_B,
                   id="nl", topPadding=0, bottomPadding=0, leftPadding=0, rightPadding=0)
        r2 = Frame(MARGIN_L+COL_W+COL_GAP, MARGIN_B, COL_W, PAGE_H-MARGIN_T-MARGIN_B,
                   id="nr", topPadding=0, bottomPadding=0, leftPadding=0, rightPadding=0)
        self.addPageTemplates([
            PageTemplate(id="P1", frames=[tf, c1, c2], onPage=pg1),
            PageTemplate(id="PN", frames=[l2, r2],     onPage=pgN),
        ])

# ══════════════════════════════════════════════════════════════════════════════
def build():
    story = [NextPageTemplate("PN")]

    # ── TOP FRAME ──
    story.append(Paragraph(
        "LifeLink AI: A Trustworthy Hybrid Clinical Decision-Support Architecture "
        "for Real-Time Emergency Blood Matching in Digital and Precise Medicine", TTL))
    story.append(Paragraph(
        "Shivang Mishra, Lakshya Sahu, Kushagra Bhargava, Anshul, Archisha Nigam, Mokshi Jain", AUT))
    story.append(Paragraph("VIT Bhopal University, Bhopal, India", AFF))
    story.append(sp(3)); story.append(HR()); story.append(sp(2))

    story.append(Paragraph(
        "<b><i>Abstract</i></b>\u2014Emergency blood provision during acute haemorrhagic trauma, "
        "perioperative crises, and obstetric complications demands sub-minute coordination under "
        "uncompromising patient-safety constraints. Conventional procurement relies on fragmented "
        "telephonic cascades and static web directories, introducing latencies of 20\u201360 minutes "
        "that substantially elevate mortality within the \u2018golden hour.\u2019 This paper presents "
        "<b>LifeLink AI</b>, a trustworthy hybrid clinical decision-support architecture for real-time "
        "emergency blood matching in Digital and Precise Medicine. The system implements a formally "
        "defined <b>two-layer safety contract</b>: Layer\u00a01 enforces an immunohematological "
        "verification gate\u2014O(1) ABO/Rh compatibility look-up, a mandatory 56-day whole-blood "
        "recovery cooldown, and a minimum 45\u00a0kg body-mass constraint\u2014that is computationally "
        "isolated from any machine-learning component. Layer\u00a02 applies a calibrated logistic-"
        "regression donor-response propensity model, whose sole purpose is to rank Layer-1-qualified "
        "candidates by their estimated willingness to respond to an emergency alert. The propensity "
        "model is trained on the UCI Blood Transfusion Service Center benchmark (748 records, 5-fold "
        "stratified CV) and achieves ROC-AUC\u202f=\u202f0.7521, Recall\u202f=\u202f0.7528, "
        "Precision\u202f=\u202f0.3907, F1\u202f=\u202f0.5144, and Brier Score\u202f=\u202f0.2055. "
        "The platform is containerised across six microservices and validated by 56 automated "
        "integration tests (100% pass rate). Matching latencies are 47.2\u00a0ms (AI path) and "
        "12.4\u00a0ms (deterministic fallback). LifeLink AI demonstrates how a strict architectural "
        "boundary between deterministic medical logic and probabilistic AI can bridge critical "
        "logistics bottlenecks in emergency precision healthcare while maintaining non-negotiable "
        "patient-safety guarantees.", ABS))
    story.append(sp(2))
    story.append(Paragraph(
        "<b><i>Keywords</i></b>\u2014Digital and precise medicine; trustworthy AI; clinical decision "
        "support; emergency blood matching; immunohematology; donor response propensity; hybrid "
        "architecture; logistic regression; RFM model; microservices.", ABS))
    story.append(sp(2)); story.append(HR())
    story.append(FrameBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # I. INTRODUCTION
    # ══════════════════════════════════════════════════════════════════════════
    story.append(sec("I", "INTRODUCTION"))
    story.append(s(
        "Haemorrhagic shock secondary to traumatic injury, postpartum haemorrhage, major cardiovascular "
        "surgery, and acute oncological cytopenias represents one of the foremost causes of preventable "
        "mortality in emergency medicine worldwide [1]. Clinical evidence across trauma resuscitation "
        "consistently demonstrates that patient survival probability decays non-linearly as "
        "time-to-transfusion increases; within the critical \u2018golden hour,\u2019 every additional "
        "ten-minute delay in procuring cross-match-compatible blood units correlates with exponential "
        "increases in multiorgan failure risk and mortality [2]. The coagulopathic lethal triad of "
        "hypothermia, acidosis, and coagulopathy rapidly becomes irreversible without rapid blood "
        "product infusion, making the speed and accuracy of blood matching a direct determinant of "
        "patient outcomes in emergency care settings."))
    story.append(s(
        "Globally, the World Health Organization (WHO) estimates that approximately 118.5 million "
        "blood donations are collected annually, yet profound and often lethal disparities persist in "
        "the logistical distribution and emergency allocation of blood products across regional "
        "healthcare networks [3]. In India, where annual blood demand approaches 14 million units "
        "against an estimated collection of 12 to 15 million units [4], the clinical challenge is "
        "rarely an absolute national shortage; rather, it is a severe structural and temporal "
        "coordination failure caused by geographic maldistribution, cold-chain fragmentation, and "
        "pervasive information asymmetry across regional healthcare providers."))
    story.append(s(
        "Emergency blood procurement across municipal healthcare networks currently suffers from "
        "three compounding structural defects that collectively drive dangerous dispatch latencies: "
        "(i)\u00a0<i>Uncoordinated telephonic cascades</i> across regional blood banks and voluntary "
        "donor lists, consuming 20\u201360 minutes per requisition without any real-time verification "
        "of stock availability; (ii)\u00a0<i>Static directories with no real-time inventory "
        "visibility</i>, causing high rejection rates as coordinators contact facilities with "
        "exhausted or incompatible stocks; and (iii)\u00a0<i>Undifferentiated donor contact lists</i> "
        "that ignore historical donation recency, frequency, and geographic transit times, wasting "
        "critical minutes on individuals statistically unlikely to respond within the therapeutic window."))
    story.append(s(
        "Addressing these bottlenecks requires an engineering approach grounded in "
        "<b>Digital and Precise Medicine</b>\u2014the application of algorithmic and computational "
        "precision to the logistics of life-saving biological products under acute temporal "
        "constraints. However, introducing artificial intelligence into emergency medicine creates "
        "substantial clinical and medicolegal risks. Machine learning models deployed in high-stakes "
        "clinical workflows are susceptible to distribution shifts, probabilistic overconfidence, "
        "and catastrophic failure under rare-event conditions [12]. In blood transfusion specifically, "
        "an algorithmic error recommending an ABO-incompatible unit can induce acute intravascular "
        "haemolysis, acute kidney injury, systemic inflammatory shock, and death within minutes of "
        "infusion. No probabilistic model\u2014regardless of its training performance\u2014can be "
        "permitted to govern this immunohematological determination."))
    story.append(s(
        "To resolve this fundamental tension between algorithmic efficiency and inviolable patient "
        "safety, this paper presents <b>LifeLink AI</b>, a trustworthy hybrid clinical "
        "decision-support system. LifeLink AI implements a <b>two-layer safety contract</b> that "
        "enforces an absolute, computationally enforced boundary: biological compatibility and "
        "statutory eligibility are governed exclusively by deterministic medical logic, while "
        "machine learning operates entirely as an advisory donor-response propensity layer that "
        "influences only operational ranking\u2014never medical safety decisions."))
    story.append(s("<b>Research Contributions:</b>", False))
    story.append(bul("<i>Two-Layer Safety Contract</i>\u2014a formalised pattern that isolates zero-tolerance medical invariants from probabilistic AI across containerised network boundaries."))
    story.append(bul("<i>Hybrid Composite Scoring</i>\u2014an interpretable ranking function integrating compatibility quality, PostGIS geospatial proximity, operational availability, and AI response propensity."))
    story.append(bul("<i>Calibrated ML Propensity Model</i>\u2014balanced logistic regression on the UCI BTSC benchmark, prioritising clinical recall (0.7528) over raw accuracy."))
    story.append(bul("<i>Production-Grade Validation</i>\u201456 automated integration tests (100% pass), sub-100\u00a0ms latencies, and pessimistic SELECT\u2026FOR UPDATE concurrency locking."))
    story.append(bul("<i>ReBAC Governance</i>\u2014a 7-role multi-tenant access model with immutable audit logging."))

    # ══════════════════════════════════════════════════════════════════════════
    # II. RELATED WORK
    # ══════════════════════════════════════════════════════════════════════════
    story.append(sec("II", "RELATED WORK"))
    story.append(sub("A", "Blood Supply Chain Logistics"))
    story.append(s(
        "The management of human blood products has been extensively studied as a perishable "
        "inventory routing problem exhibiting severe time-temperature constraints, stochastic demand, "
        "and heterogeneous supply points. Stanger et al. [5] surveyed inventory management strategies "
        "across European transfusion services, identifying that blood wastage (outdating) and acute "
        "supply shortages stem primarily from fragmented inventory visibility and non-integrated "
        "ordering systems across regional hospital networks. Early technological interventions "
        "focused on computerized physician order entry (CPOE). Heitmiller et al. [6] demonstrated "
        "that algorithmic clinical guidelines embedded within ordering software reduced unnecessary "
        "cross-matches by 42% and significantly shortened procurement turnaround times in elective "
        "surgical settings."))
    story.append(s(
        "In recent years, Internet of Things (IoT) sensor networks and RFID tagging have been "
        "introduced to automate cold-chain tracking, temperature excursion monitoring, and "
        "barcode-driven chain-of-custody [7]. However, these systems address static facility "
        "inventory management and supply-chain traceability rather than dynamic, real-time "
        "multi-facility emergency coordination across voluntary donor populations during acute "
        "trauma events. In India, the government-backed e-Rakt Kosh platform [8] provides "
        "centralised web directories of licensed blood banks, but functions as a passive "
        "administrative registry lacking automated spatial candidate matching, real-time donor "
        "availability verification, and predictive response modelling."))
    story.append(sub("B", "Machine Learning in Donor Behaviour"))
    story.append(s(
        "Predicting donor lapse, return probability, and emergency response behaviour has engaged "
        "the data science and transfusion medicine communities since Yeh et al. [9] published the "
        "foundational RFM (Recency, Frequency, Monetary) framework for blood donation. Their "
        "empirical study on 748 Blood Transfusion Service Center (BTSC) records established that "
        "recent and frequent donors exhibit measurably higher future response propensity, yielding "
        "a population-level positive class prevalence of 23.8%\u2014a pronounced class imbalance "
        "that fundamentally motivates the balanced class-weight strategy adopted in LifeLink AI. "
        "Gilliss et al. [10] evaluated artificial neural networks and logistic regression for "
        "predicting first-time donor return rates, confirming that timely, targeted outreach and "
        "operational convenience are dominant predictors of donor loyalty."))
    story.append(s(
        "Meta-analyses of classifier performance on donor retention datasets [11] reveal that while "
        "complex non-linear ensemble models occasionally yield marginal gains in area under the ROC "
        "curve, regularised logistic regression consistently provides superior probability "
        "calibration, monotonic score stability, and model-level intrinsic interpretability when "
        "operating on low-dimensional behavioural feature sets\u2014a critical advantage in "
        "safety-critical clinical applications where model transparency is non-negotiable. "
        "Ramachandran et al. [18] corroborated this finding, observing that unconstrained deep "
        "neural networks exhibit unreliable out-of-distribution behaviour in medical logistics "
        "tasks, recommending calibrated linear models for domains where worst-case failure carries "
        "irreversible consequences."))
    story.append(sub("C", "Trustworthy AI in Healthcare"))
    story.append(s(
        "The translation of artificial intelligence from benchmark research into frontline clinical "
        "practice is severely constrained by the \u2018black box\u2019 problem. In high-stakes medicine, "
        "clinicians, transfusion coordinators, and hospital ethics committees cannot accept opaque "
        "recommendations from deep neural networks without verifiable causal justifications [12], [17]. "
        "Rudin [12] argued that interpretable models should be adopted in high-stakes decisions "
        "wherever possible, demonstrating that intrinsic interpretability frequently achieves "
        "competitive predictive performance while eliminating the opacity and instability risks "
        "inherent to black-box ensembles. Doshi-Velez and Kim [16] formalised the distinction "
        "between post-hoc interpretability (LIME, SHAP approximations) and intrinsic "
        "interpretability, where model equations are directly comprehensible to domain experts "
        "without secondary approximations that may themselves introduce distortions."))
    story.append(s(
        "The EU High-Level Expert Group on AI [13] and the IEEE Ethically Aligned Design [14] "
        "formulated overlapping core tenets for Trustworthy AI: clinical validity, non-maleficence, "
        "transparency, accountability, and robustness. The EU AI Act [15] further classifies medical "
        "decision-support systems with direct patient impact as high-risk, requiring mandatory "
        "conformity assessment, audit logging, and human oversight before deployment. LifeLink AI "
        "operationalises these principles through: (a)\u00a0architecturally enforced determinism "
        "for biological safety decisions; (b)\u00a0a three-level resilient fallback hierarchy; "
        "(c)\u00a0immutable audit logs of every matching decision; and (d)\u00a0human-in-the-loop "
        "dispatch retaining final authority with qualified clinicians [19], [20]."))

    story.append(s("<b>Comparative Positioning.</b> Table\u00a0I contrasts LifeLink AI "
                   "against representative prior systems. LifeLink AI is the only system "
                   "combining O(1) deterministic compatibility guarantees, intrinsically "
                   "interpretable AI ranking, a three-level fallback hierarchy, and pessimistic "
                   "concurrency control.", False))

    comp_cap = Paragraph("TABLE I\u2014ARCHITECTURE COMPARISON", TCAP)
    comp_tbl = tbl([
        ["Dimension",      "Static Reg.",     "Pure ML",       "LifeLink AI"],
        ["Compatibility",  "Manual",          "Probabilistic", "Det. O(1) Gate"],
        ["Donor Priority", "FIFO",            "Black-Box",     "Calibrated LR"],
        ["Explainability", "N/A",             "Post-Hoc",      "Intrinsic"],
        ["Fallback",       "Manual",          "Unhandled",     "3-Level Chain"],
        ["Concurrency",    "None",            "None",          "FOR UPDATE Lock"],
        ["Audit Trail",    "None",            "Informal",      "Immutable Ledger"],
    ], cw=[0.82*inch, 0.68*inch, 0.68*inch, COL_W-2.18*inch], center=[1,2,3])
    story.append(KeepTogether([comp_cap, comp_tbl])); story.append(sp(3))

    # ══════════════════════════════════════════════════════════════════════════
    # III. PROBLEM FORMULATION AND SYSTEM MODEL
    # ══════════════════════════════════════════════════════════════════════════
    story.append(sec("III", "PROBLEM FORMULATION AND SYSTEM MODEL"))
    story.append(sub("A", "Emergency Request"))
    story.append(s("A blood requisition is defined as the typed tuple:"))
    story.append(eq(
        "E = (req\u1d35\u1d48, \u03b2\u1d3f\u1d49\u1d9c, \u03b3, "
        "u\u1d3f\u1d49\u1d52, \u03bb\u1d48\u1d49\u02e2\u1d57, \u03c9, t\u2080)",
        "(1)"))
    story.append(s(
        "where \u03b2\u1d3f\u1d49\u1d9c \u2208 \u212c = {O\u00b1, A\u00b1, B\u00b1, AB\u00b1} "
        "is the recipient blood group; \u03b3 is the prescribed component "
        "(Whole Blood, RBC, Plasma, Platelets); u\u1d3f\u1d49\u1d52 \u2208 [1,\u202020] is "
        "the requested units; \u03bb\u1d48\u1d49\u02e2\u1d57 = (\u03c6, \u03c8) are WGS-84 "
        "geospatial coordinates; \u03c9 \u2208 {LOW, MED, HIGH, CRITICAL} is urgency; "
        "and t\u2080 is the UTC submission timestamp."))
    story.append(sub("B", "Candidate Pools and Notation"))
    story.append(s(
        "Registered voluntary donors \u03a9\u1d30 = {d\u2081,\u2026,d\u2099} and licensed "
        "blood banks \u03a9\u1d37 = {k\u2081,\u2026,k\u1d39} are indexed by PostGIS GiST "
        "geometry columns (SRID\u00a04326). Each donor is parameterised by "
        "d\u1d35 = (\u03b2\u1d35, w\u1d35, a\u1d35, e\u1d35, \u03bb\u1d35, "
        "t\u2097\u2090\u02e2\u1d57, F\u1d35, T\u1d35) where w\u1d35 (kg) is body mass, "
        "a\u1d35, e\u1d35 \u2208 {0,\u20091} are availability and eligibility flags, "
        "and (F\u1d35, T\u1d35) are RFM behavioural features. "
        "Table\u00a0II summarises key notation."))

    not_cap = Paragraph("TABLE II\u2014KEY NOTATION", TCAP)
    not_tbl = tbl([
        ["Symbol",                   "Domain",          "Meaning"],
        ["\u03b2\u1d3f\u1d49\u1d9c, \u03b2\u1d48\u1d52\u207f", "\u212c", "Recipient/donor ABO/Rh group"],
        ["\u03bb = (\u03c6, \u03c8)", "WGS-84",         "Geospatial coordinates"],
        ["d\u2095\u2090\u1d65(\u03bb\u2081,\u03bb\u2082)", "km", "Haversine great-circle distance"],
        ["R\u209b\u1d49\u2090\u1d3f\u1d9c\u02b0", "{15,25,50,100}\u00a0km", "Active spatial radius"],
        ["\u0394t\u1d9c\u1d52\u1d52\u02e1",  "\u226556\u00a0days", "Whole-blood recovery cooldown"],
        ["P\u1d39\u1caC",             "[0,\u20091]",      "Logistic regression propensity score"],
        ["P\u209a\u1d49\u1d52",        "[0,\u20091]",      "Linear spatial proximity decay"],
        ["S\u1d48\u1d52\u207f\u1d52\u1d3f", "[0,\u20091]", "Composite donor ranking score"],
        ["S\u1d47\u1d47",              "[0,\u20091]",      "Composite blood bank ranking score"],
        ["\u03b1\u2081, \u03b1\u2080","\u211d\u207a",     "Balanced inverse class-frequency weights"],
    ], cw=[0.85*inch, 0.80*inch, COL_W-1.65*inch])
    story.append(KeepTogether([not_cap, not_tbl])); story.append(sp(3))

    story.append(sub("C", "Clinical Problem Constraints and Matching Objective"))
    story.append(s(
        "The blood matching optimisation problem must simultaneously satisfy four non-negotiable "
        "constraint categories: "
        "<i>(1) Immunohematological Safety</i>\u2014only ABO/Rh-compatible donors or blood banks "
        "may appear in any ranked output; incompatibility is a binary hard constraint that "
        "overrides all scoring signals. "
        "<i>(2) Donor Physiological Eligibility</i>\u2014statutory minimum body mass (\u2265\u00a045\u00a0kg), "
        "mandatory 56-day recovery cooldown between whole-blood donations (WHO standard), "
        "and self-declared availability at the time of the emergency request. "
        "<i>(3) Inventory Sufficiency and Non-Preemption</i>\u2014blood bank candidates are "
        "valid only if their current unreserved stock of the compatible component meets or "
        "exceeds u_req, and reserved units must be protected against double-allocation by "
        "concurrent requests. "
        "<i>(4) Temporal Urgency</i>\u2014the entire matching pipeline, from emergency request "
        "receipt to ranked candidate notification, must complete within a latency budget "
        "compatible with dispatch in the clinical golden hour."))
    story.append(s(
        "The matching objective is to produce two ranked lists for each emergency requisition "
        "E: (a)\u00a0a ranked list of at most K\u1d30 voluntary donors "
        "{d\u1d35 : Gate(d\u1d35) = 1} ordered by S_donor (Eq.\u00a06); and "
        "(b)\u00a0a ranked list of at most K\u1d37 blood banks "
        "{k\u1d35 : Stock_score(k\u1d35) > 0} ordered by S_bb (Eq.\u00a07). "
        "Both lists are presented to the emergency coordinator, who retains the authority "
        "to override the algorithmic ordering based on clinical context, real-time "
        "communications, or institutional relationships."))

    # ══════════════════════════════════════════════════════════════════════════
    # IV. PROPOSED METHODOLOGY AND SAFETY ARCHITECTURE
    # ══════════════════════════════════════════════════════════════════════════
    story.append(sec("IV", "PROPOSED METHODOLOGY AND SAFETY ARCHITECTURE"))
    story.append(sub("A", "The Two-Layer Safety Contract"))
    story.append(s(
        "The central design principle of LifeLink AI is a formally defined and architecturally "
        "enforced <b>two-layer safety contract</b>, illustrated in Fig.\u00a01. This contract "
        "separates medical safety decisions from operational efficiency decisions at the "
        "container-network boundary level. <i>Layer\u00a01</i> is the Deterministic Medical "
        "and Statutory Eligibility Gate: it applies immunohematological compatibility rules, "
        "physiological thresholds, statutory donation intervals, and availability checks "
        "entirely within the backend service, with no dependence on the AI microservice. "
        "<i>Layer\u00a02</i> is the AI-Assisted Operational Ranking Layer: it applies the "
        "calibrated logistic regression propensity estimator and the multi-criteria composite "
        "scoring functions exclusively to the set of candidates that have already passed "
        "Layer\u00a01. The two layers communicate only through a well-defined data contract "
        "(a list of candidate identifiers) that flows from Layer\u00a01 to Layer\u00a02, "
        "never in the reverse direction."))
    story.append(s(
        "The clinical rationale for this separation is non-negotiable: probabilistic models "
        "can produce erroneous outputs under distribution shift, adversarial inputs, or "
        "unexpected feature combinations. In blood transfusion, any such error that reaches "
        "the compatibility determination could produce a recommendation of an ABO-incompatible "
        "unit, with lethal consequences for the patient. By confining all AI outputs to the "
        "Layer-2 ranking domain\u2014where errors cause suboptimal ordering rather than "
        "biological harm\u2014LifeLink AI provides a formal safety guarantee that is "
        "independent of model performance: no AI output, regardless of its value, can "
        "ever cause an incompatible candidate to appear in the output."))

    if FIG1_PATH.exists():
        fig_img = Image(str(FIG1_PATH), width=COL_W, height=1.65*inch)
        fig_cap = Paragraph(
            "<i>Fig.\u00a01.</i> LifeLink AI two-layer safety contract. Layer\u00a01 enforces "
            "deterministic immunohematological and statutory eligibility gates. Layer\u00a02 applies "
            "calibrated AI propensity scoring for advisory ranking only. Medical safety decisions are "
            "exclusively Layer-1 outputs.", FCAP)
        story.append(KeepTogether([fig_img, fig_cap]))

    story.append(sub("B", "Layer 1: Deterministic Medical Compatibility Gate"))
    story.append(s(
        "Immunohematological compatibility is governed by the ABO/Rh blood group antigen-antibody "
        "system: an O-group recipient can only receive O-group red cells; an A-group recipient can "
        "receive A-group or O-group red cells; a B-group recipient can receive B-group or "
        "O-group cells; and an AB-group recipient is the universal receiver. The Rh factor "
        "adds a parallel constraint: Rh\u2212 recipients can only receive Rh\u2212 blood, "
        "while Rh\u207a recipients can receive either polarity. ABO incompatibility triggers "
        "immediate complement activation and acute intravascular haemolysis, which can be "
        "fatal within minutes of infusion. This biological law is implemented as a "
        "pure-Python, ML-free O(1) set-theoretic dictionary look-up in "
        "<i>backend/app/core/medical.py</i>. For Whole Blood and PRBC:"))
    story.append(eq(
        "C\u1d3f\u1d2e\u1d9c(\u03b2\u1d3f\u1d49\u1d9c) = "
        "{\u03b2\u1d48\u1d52\u207f \u2208 \u212c \u2223 donor RBC compatible with \u03b2\u1d3f\u1d49\u1d9c}", "(2)"))
    story.append(s("For FFP, donor antibody profile inverts compatibility (AB \u2192 universal donor):"))
    story.append(eq(
        "C\u1d3a\u02e1\u2090\u02e2\u1d39\u2090(\u03b2\u1d3f\u1d49\u1d9c) = "
        "{\u03b2\u1d48\u1d52\u207f \u2208 \u212c \u2223 donor plasma compatible with \u03b2\u1d3f\u1d49\u1d9c}", "(3)"))
    story.append(s("A donor d\u1d35 passes Layer\u00a01 if and only if all five predicates are satisfied:"))
    story.append(eq(
        "Gate(d\u1d35) = [\u03b2\u1d35 \u2208 C] \u2227 [e\u1d35=1] \u2227 [a\u1d35=1] "
        "\u2227 [\u0394t\u1d9c\u1d52\u1d52\u02e1 \u2265 56] \u2227 [w\u1d35 \u2265 45]", "(4)"))
    story.append(s(
        "The 56-day cooldown is the WHO-mandated minimum inter-donation interval for "
        "whole blood, implemented by computing the difference between the system timestamp "
        "and the donor\u2019s last donation date stored in the PostgreSQL schema. The 45\u00a0kg "
        "minimum body mass reflects clinical consensus that donors below this threshold face "
        "elevated hypovolaemia risk; it is enforced at two levels: by application logic "
        "computing Gate(d\u1d35), and by a PostgreSQL CHECK constraint that prevents any "
        "donor record with weight_kg < 45 from being committed to the database. Donors "
        "failing any single predicate of the conjunction are unconditionally excluded from "
        "the candidate pool before any scoring computation begins."))

    story.append(sub("C", "Layer 2: Multi-Criteria Composite Ranking"))
    story.append(s(
        "Spatial proximity is quantified by the Haversine great-circle metric "
        "d_hav(\u03bb\u2081, \u03bb\u2082), computed in the PostgreSQL tier via "
        "ST_DWithin on GiST-indexed geometry columns. Proximity decays linearly over "
        "the active search radius R_search \u2208 {15, 25, 50, 100}\u00a0km, selected "
        "adaptively by the coordinator based on urgency:"))
    story.append(eq("P\u209a\u1d49\u1d52 = max(0,\u00a01 \u2212 d\u2095\u2090\u1d65/R\u209b\u1d49\u2090\u1d3f\u1d9c\u02b0)", "(5)"))
    story.append(s(
        "The composite donor score integrates four orthogonal signals into a single "
        "[0,\u20091]-bounded ranking metric:"))
    story.append(eq(
        "S\u1d48\u1d52\u207f\u1d52\u1d3f = 0.40\u00a0C\u209b\u1d9c\u1d52\u1d3f\u1d49 "
        "+ 0.30\u00a0P\u209a\u1d49\u1d52 + 0.20\u00a0A\u209b\u1d9c\u1d52\u1d3f\u1d49 "
        "+ 0.10\u00a0P\u1d39\u1caC", "(6)"))
    story.append(s(
        "where C\u209b\u1d9c\u1d52\u1d3f\u1d49 = 1.0 for exact ABO/Rh match (0.8 for universal "
        "compatible donor); A\u209b\u1d9c\u1d52\u1d3f\u1d49 = 1.0 for currently available donors; "
        "and P\u1d39\u1caC is the calibrated AI propensity probability. The weight assignments "
        "reflect deliberate clinical priorities: compatibility quality (0.40) dominates because "
        "exact blood group matching minimises the risk of alloimmunisation over repeat "
        "transfusions; proximity (0.30) dominates over availability and propensity because "
        "travel time is a primary practical constraint in emergency procurement; availability "
        "(0.20) ensures present commitment; and AI propensity (0.10) provides evidence-based "
        "uplift that stratifies candidates with otherwise similar scores without dominating "
        "the medically critical factors. For blood banks, stock sufficiency replaces propensity:"))
    story.append(eq(
        "S\u1d47\u1d47 = 0.40\u00a0C\u209b\u1d9c\u1d52\u1d3f\u1d49 "
        "+ 0.35\u00a0Stock\u209b\u1d9c\u1d52\u1d3f\u1d49 + 0.25\u00a0P\u209a\u1d49\u1d52", "(7)"))
    story.append(s(
        "where Stock\u209b\u1d9c\u1d52\u1d3f\u1d49 = min(1, u\u2090\u1d65\u2090\u1d35\u02e1/u\u1d3f\u1d49\u1d52). "
        "For blood banks, stock sufficiency carries the highest weight (0.35) because "
        "institutional stock availability is the primary operational determinant; proximity "
        "(0.25) is weighted lower than for donors because blood bank facilities are "
        "generally more numerous and geographically distributed, making stock the dominant "
        "discriminating factor among candidate institutions."))

    # ══════════════════════════════════════════════════════════════════════════
    # V. SYSTEM ARCHITECTURE AND IMPLEMENTATION
    # ══════════════════════════════════════════════════════════════════════════
    story.append(sec("V", "SYSTEM ARCHITECTURE AND IMPLEMENTATION"))
    story.append(sub("A", "Microservice Topology"))
    story.append(s(
        "LifeLink AI is containerised across six isolated Docker services, each with a strictly "
        "defined responsibility boundary and network exposure policy. "
        "<b>lifelink-nginx</b> (port 80) serves as the reverse proxy, providing SSL termination, "
        "request routing, and rate limiting to shield upstream services. "
        "<b>lifelink-frontend</b> (port 3000) implements the Next.js 14.2.5 App Router "
        "single-page application, serving role-specific user interfaces for donors, hospital "
        "administrators, blood bank managers, and system administrators. "
        "<b>lifelink-backend</b> (port 8000) implements the FastAPI 0.111.1 orchestration "
        "engine on Python 3.11, executing all business logic, coordinating the matching "
        "pipeline, and managing all database transactions. "
        "<b>lifelink-ai-service</b> (port 8001) is a dedicated scikit-learn 1.5.1 inference "
        "microservice that executes the calibrated logistic regression model in an isolated "
        "process context, enforcing the Layer-2 computational boundary. "
        "<b>lifelink-postgres</b> (port 5432) provides PostgreSQL 15 with PostGIS 3.3 as the "
        "system of record. "
        "<b>lifelink-redis</b> (port 6379) serves Redis 7 as a session cache and API "
        "rate-limiter. All inter-service traffic runs on an isolated Docker bridge network; "
        "only Nginx exposes a public port. The AI service occupies its own isolated container, "
        "enforcing the Layer-1/Layer-2 separation at the OS process boundary."))
    story.append(sub("B", "Database Schema and Concurrency Control"))
    story.append(s(
        "The database architecture comprises 11 relational tables managed under migration "
        "control: <i>users</i>, <i>user_roles</i>, <i>donors</i>, <i>hospitals</i>, "
        "<i>blood_banks</i>, <i>blood_inventory</i>, <i>inventory_history</i>, "
        "<i>emergency_requests</i>, <i>match_runs</i>, <i>match_candidates</i>, and "
        "<i>donor_emergency_responses</i>. Spatial attributes (location_geom) are stored as "
        "native PostGIS geometry objects with SRID=4326 (WGS-84) and indexed using "
        "Generalized Search Trees (GiST), enabling O(log N) bounding box and great-circle "
        "radius queries via ST_DWithin. Database-level CHECK constraints enforce physiological "
        "bounds (weight_kg \u2265 45; units_required between 1 and 20). The "
        "<i>inventory_history</i> table operates as an immutable append-only audit "
        "ledger\u2014UPDATE and DELETE operations are disallowed at the database role "
        "level\u2014guaranteeing complete traceability for every blood unit reserved, "
        "released, or dispatched."))
    story.append(s(
        "Under concurrent emergency conditions, multiple hospitals in a metropolitan area "
        "may simultaneously submit requests for the same rare blood group (e.g., AB\u2212, "
        "present in approximately 0.6% of the Indian population). Without explicit concurrency "
        "control, two concurrent PostgreSQL transactions could both read a non-zero available "
        "stock, both commit reservations, and jointly produce an over-allocation that drives "
        "effective availability below zero. LifeLink AI prevents this anomaly through "
        "<b>pessimistic row-level locking</b> via SELECT\u2026FOR UPDATE. The acquired "
        "exclusive row lock serialises competing transactions: the locked transaction "
        "increments units_reserved, validates that units_available \u2212 units_reserved "
        "\u2265 u_req, commits atomically, and writes an immutable inventory audit record. "
        "Any competing transaction attempting to lock the same row blocks until the first "
        "transaction commits or rolls back, guaranteeing linearizability of inventory state."))
    story.append(sub("C", "Security and Access Control"))
    story.append(s(
        "A 7-role Relationship-Based Access Control (ReBAC) hierarchy "
        "(SUPER_ADMIN \u2192 ADMIN \u2192 {HOSPITAL_ADMIN, BB_MANAGER} \u2192 staff \u2192 DONOR) "
        "is enforced at three independent layers: "
        "(1) JWT HMAC-SHA256 signature verification with 30-minute access tokens and 7-day "
        "rolling refresh tokens; "
        "(2) FastAPI dependency injection validating role membership and institutional "
        "tenancy\u2014cross-tenant access is rejected with HTTP 403 before any database query "
        "executes; and "
        "(3) SQLAlchemy query filters scoping all data retrieval to the requesting user\u2019s "
        "institutional identifier. Patient PII on public tracking portals is protected by "
        "cryptographic UUID tokens derived from req_id, shielding patient identities from "
        "public-facing URLs."))
    story.append(s(
        "<i>Facility Verification Boundary:</i> Hospitals and blood banks register statutory "
        "identifiers (CDSCO/SBTC registration numbers), license issue/expiry dates, and "
        "upload digital certificate PDFs. The platform stores and organises these documents "
        "for administrative governance review; it does <i>not</i> validate license numbers "
        "against live external government APIs in the current implementation. This design "
        "decouples the one-time institutional onboarding trust process from the real-time "
        "emergency matching pipeline, preventing external API latency from degrading "
        "emergency dispatch response times."))

    # ══════════════════════════════════════════════════════════════════════════
    # VI. AI DONOR RESPONSE PROPENSITY MODEL
    # ══════════════════════════════════════════════════════════════════════════
    story.append(sec("VI", "AI DONOR RESPONSE PROPENSITY MODEL"))
    story.append(sub("A", "Role and Clinical Boundaries"))
    story.append(s(
        "The AI component is an <b>advisory response propensity estimator</b>. Its sole function "
        "is to estimate the conditional probability that a Layer-1-qualified donor will accept an "
        "emergency alert and travel to the collection centre. It does <i>not</i> determine blood "
        "compatibility, assess medical eligibility, diagnose patients, or initiate dispatch. "
        "The AI service receives only behavioural features (R, F, T) and returns only "
        "P\u1d39\u1caC \u2208 [0,\u20091]; it cannot read blood group data."))
    story.append(sub("B", "Dataset and Feature Engineering"))
    story.append(s(
        "The propensity model is trained on the UCI Blood Transfusion Service Center (BTSC) "
        "benchmark [9] (OpenML dataset ID 1464, CC BY 4.0 licence), a widely-used reference "
        "dataset in donor behaviour modelling comprising N\u00a0=\u00a0748 anonymised records "
        "from a mobile blood collection unit in Hsin-Chu City, Taiwan. The positive class "
        "(donated in March 2007: 178 records, 23.8%) and negative class (did not donate: "
        "570 records, 76.2%) constitute a 3.2:1 class imbalance representative of active "
        "blood donor populations. The four original features are: "
        "<i>Recency</i> (R)\u2014months since last donation; "
        "<i>Frequency</i> (F)\u2014total lifetime donations; "
        "<i>Monetary</i> (M)\u2014total blood donated in cubic centimetres (M\u202f=\u202f250F, "
        "as each donation is a fixed 250\u00a0cc unit); and "
        "<i>Time</i> (T)\u2014months since first donation."))
    story.append(s(
        "Statistical analysis of the feature correlation matrix reveals exact multicollinearity: "
        "M = 250F yields Pearson r\u202f=\u202f1.000 and Spearman \u03c1\u202f=\u202f1.000. "
        "Retaining M alongside F would produce a rank-deficient Gram matrix G = X\u1d40X, "
        "preventing L-BFGS optimisation from converging to a unique weight vector. Accordingly, "
        "M is pruned, yielding the three-dimensional RFT feature vector "
        "<b>x</b> = [R, F, T]\u1d40 \u2208 \u211d\u00b3. "
        "The 5-fold Stratified CV (SKF-CV) cross-validation procedure ensures that the "
        "23.8%/76.2% class distribution is preserved identically in every training and test "
        "fold, and that the StandardScaler parameters (\u03bc, \u03a3) are fit exclusively on "
        "training folds and applied without refitting to corresponding test folds, eliminating "
        "any possibility of data leakage."))
    story.append(sub("C", "Model Architecture and Training"))
    story.append(s("Raw features are standardised to zero mean and unit variance:"))
    story.append(eq("<b>x</b>\u209c\u209b\u1d48 = \u03a3\u207b\u00bd (<b>x</b> \u2212 \u03bc)", "(8)"))
    story.append(s("Donor response propensity is modelled by binary logistic regression:"))
    story.append(eq(
        "P(y=1 | <b>x</b>) = \u03c3(<b>w</b>\u1d40<b>x</b>\u209c\u209b\u1d48 + b) "
        "= 1 / (1 + e\u207b(<b>w</b>\u1d40<b>x</b>\u209c\u209b\u1d48 + b))", "(9)"))
    story.append(s(
        "To counteract the 3.2:1 class imbalance, the binary cross-entropy loss function "
        "is augmented with balanced inverse class-frequency weights:"))
    story.append(eq(
        "L(<b>w</b>,b) = \u2212(1/N)\u03a3 [\u03b1\u2081 y\u1d35 log p\u1d35 "
        "+ \u03b1\u2080(1\u2212y\u1d35) log(1\u2212p\u1d35)] + (\u03bb/2)\u2016<b>w</b>\u2016\u00b2", "(10)"))
    story.append(eq(
        "\u03b1\u2081 = N/(2N\u208a) = 2.101,\u2003 \u03b1\u2080 = N/(2N\u208b) = 0.656", "(11)"))
    story.append(s(
        "The weight \u03b1\u2081\u202f>\u202f1 penalises False Negatives (failing to identify a "
        "willing donor who would have responded) more heavily than False Positives (alerting a "
        "donor who ultimately declines). This asymmetry reflects the clinical cost structure of "
        "emergency blood dispatch: a missed willing donor may delay transfusion by the full "
        "time required to contact the next candidate, with direct survival consequences, "
        "whereas a spurious alert causes only minor notification friction. The L2 regularisation "
        "term (\u03bb\u202f=\u202f1/C\u202f=\u202f1.0) prevents overfitting on the 748-record "
        "dataset. Parameter optimisation uses the L-BFGS quasi-Newton algorithm."))
    story.append(sub("D", "Three-Level Resilient Fallback"))
    story.append(s(
        "To guarantee uninterrupted operation under infrastructure failures: "
        "<b>(1)\u00a0Primary</b>\u2014full calibrated inference via the AI microservice; "
        "<b>(2)\u00a0Secondary</b> (service reachable, model fails)\u2014in-process closed-form "
        "RFM heuristic:"))
    story.append(eq(
        "P\u209f\u1d47 = min(0.95, max(0.05, 0.40 + max(0, 0.35\u22120.01R) + min(0.25, 0.05F)))", "(12)"))
    story.append(s(
        "<b>(3)\u00a0Tertiary</b> (microservice unreachable)\u2014backend assigns neutral prior "
        "P\u1d39\u1caC\u202f=\u202f0.50 and records model_version\u202f=\u202f\u2018deterministic-fallback\u2019 "
        "in the audit log. The matching pipeline continues in all three levels; emergency dispatch "
        "is never halted by AI infrastructure failure."))

    # ══════════════════════════════════════════════════════════════════════════
    # VII. EXPERIMENTAL SETUP AND RESULTS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(sec("VII", "EXPERIMENTAL SETUP AND RESULTS"))
    story.append(sub("A", "Evaluation Scope"))
    story.append(s(
        "We explicitly distinguish three evaluation categories: "
        "(i)\u00a0<i>ML Model Evaluation</i>: offline 5-fold Stratified Cross-Validation (SKF-CV) "
        "on the UCI BTSC benchmark; "
        "(ii)\u00a0<i>Software Engineering Verification</i>: automated integration tests on live "
        "PostgreSQL\u00a015 + Redis\u00a07 instances in Docker Compose; "
        "(iii)\u00a0<i>Clinical Validation</i>: <b>not performed in this study</b>. LifeLink AI "
        "is a research prototype and has not undergone prospective clinical trials or regulatory "
        "clearance. Clinical and regulatory validation are prerequisites for real-world deployment."))
    story.append(sub("B", "ML Model Performance"))
    story.append(s(
        "5-fold Stratified CV (K\u202f=\u202f5, shuffle=True, random_state=42) preserves the "
        "23.8%/76.2% class distribution across all folds. StandardScaler is fit only on training "
        "folds (no data leakage). Table\u00a0III presents out-of-fold performance metrics."))

    ml_cap = Paragraph("TABLE III\u2014DONOR PROPENSITY MODEL PERFORMANCE (5-FOLD STRATIFIED CV, N\u202f=\u202f748)", TCAP)
    ml_tbl = tbl([
        ["Metric",         "Value",  "Clinical Interpretation"],
        ["Accuracy",       "0.6618", "Below majority baseline (76.2%); expected under balanced weighting"],
        ["Precision",      "0.3907", "39.1% of alerted donors are willing responders"],
        ["Recall",         "0.7528", "75.3% of willing donors correctly identified (primary objective)"],
        ["F1-Score",       "0.5144", "Harmonic balance under 3.2:1 class imbalance"],
        ["ROC-AUC",        "0.7521", "Robust discrimination; 0.50 = random, 1.00 = perfect"],
        ["PR-AUC",         "0.5028", "2.1\u00d7 improvement over naive baseline (0.238)"],
        ["Brier Score",    "0.2055", "Well-calibrated (\u00af0.25 reference)"],
    ], cw=[0.70*inch, 0.55*inch, COL_W-1.25*inch])
    story.append(KeepTogether([ml_cap, ml_tbl])); story.append(sp(2.5))

    story.append(s(
        "<b>Analysis.</b> The deliberate prioritisation of Recall over Precision through balanced "
        "weighting is grounded in the clinical cost asymmetry of emergency blood dispatch. A False "
        "Negative (the model fails to identify a willing donor) translates directly into wasted "
        "dispatch time: the coordinator must contact the next candidate, potentially delaying "
        "transfusion by several minutes in a time-critical situation. A False Positive (the "
        "system alerts a donor who ultimately declines) incurs only minor notification friction "
        "and an additional phone call. Under balanced weighting, the model correctly identifies "
        "134 of 178 willing donors (75.3%), while the remaining 44 willing donors (24.7%) are "
        "missed (False Negatives). The precision of 39.1% implies that of every 100 donors "
        "alerted, approximately 39 will respond positively\u2014a response rate substantially "
        "above that expected from undifferentiated contact lists."))
    story.append(s(
        "The PR-AUC of 0.5028 represents a 2.1\u00d7 improvement over the naive baseline "
        "classifier (0.238, equal to the positive class prevalence), confirming that the model "
        "captures genuine discriminative signal beyond random guessing on an imbalanced dataset. "
        "The Brier score of 0.2055 compares favourably to the reference no-skill Brier score "
        "of 0.2500 (a classifier always predicting the class prevalence), validating that the "
        "model\u2019s probability outputs are meaningfully calibrated for use as a propensity "
        "signal in the composite ranking score (Eq.\u00a0(6)). The ROC-AUC of 0.7521 confirms "
        "robust discrimination; values above 0.75 are generally considered clinically "
        "relevant in the donor behaviour prediction literature [9]. Preliminary experiments "
        "with random forest (n=100 estimators) and gradient-boosted classifiers yielded "
        "ROC-AUC values of 0.74\u20130.76\u2014at best a marginal improvement of 0.01 that "
        "does not justify the complete loss of intrinsic interpretability in a safety-critical "
        "context where model transparency is a regulatory and governance requirement [12]."))
    story.append(sub("C", "Integration Test Suite"))

    test_cap = Paragraph("TABLE IV\u2014INTEGRATION TEST SUITE SUMMARY (56/56 PASS)", TCAP)
    test_tbl = tbl([
        ["Test Domain",            "Count",  "Key Invariants Validated"],
        ["Auth. & ReBAC",          "8",      "JWT issuance, 7-role bounds, cross-tenant 403"],
        ["Donor & Health Gate",    "7",      "56-day cooldown, weight CHECK constraint"],
        ["Hospital Operations",    "6",      "Emergency intake schema, coordinate storage"],
        ["Blood Bank Inventory",   "6",      "Stock mgmt, certificate persistence"],
        ["Inventory Concurrency",  "7",      "FOR UPDATE locking, double-alloc. prevention"],
        ["Matching Pipeline",      "8",      "Layer-1 gate, AI scoring, HTTP-503 fallback"],
        ["Emergency Lifecycle",    "7",      "PENDING\u2192MATCHING\u2192FULFILLED transitions"],
        ["Admin Governance",       "4",      "Certificate review, facility activation"],
        ["End-to-End",             "3",      "Full cross-service dispatch flows"],
        ["<b>Total</b>",           "<b>56</b>", "<b>56/56 Passing (100%)</b>"],
    ], cw=[1.10*inch, 0.40*inch, COL_W-1.50*inch], center=[1])
    story.append(KeepTogether([test_cap, test_tbl])); story.append(sp(2.5))

    story.append(sub("D", "System Latency Benchmarking"))
    story.append(s(
        "Matching pipeline latency was measured across 100 sequential runs under Docker "
        "network virtualisation (loopback inter-container traffic), evaluating 20 candidates "
        "per requisition\u2014a representative emergency scenario. The <b>AI inference path</b> "
        "(backend calls AI microservice via HTTP/JSON on port 8001, retrieves propensity "
        "scores, computes composite scores, and returns the ranked list) achieves a mean "
        "latency of 47.2\u00a0ms (95th percentile: 83.1\u00a0ms). The <b>deterministic "
        "fallback path</b> (backend applies in-process heuristic propensity or neutral prior, "
        "no microservice HTTP round-trip) achieves mean 12.4\u00a0ms (95th percentile: "
        "21.8\u00a0ms). The 3.8\u00d7 difference in mean latency quantifies the overhead of "
        "the AI microservice HTTP round-trip under Docker network virtualisation."))
    story.append(s(
        "Both paths satisfy the sub-second (< 1000\u00a0ms) latency budget required for "
        "emergency dispatch. The 95th percentile of 83.1\u00a0ms (AI path) and 21.8\u00a0ms "
        "(fallback path) indicate reliable tail-latency performance; neither path approaches "
        "the 500\u00a0ms threshold that would be considered problematic for interactive "
        "emergency coordination workflows. The three-level fallback architecture guarantees "
        "that even under complete AI microservice failure, matching continues at "
        "12.4\u00a0ms mean latency using the deterministic heuristic or neutral prior, "
        "maintaining full operational capability for emergency dispatch throughout any "
        "AI infrastructure maintenance or failure event."))

    story.append(sec("VIII", "DISCUSSION"))
    story.append(s(
        "The central research question of this work is whether probabilistic AI can be safely "
        "integrated into emergency blood coordination without introducing unacceptable clinical "
        "risk. Our results demonstrate that this is achievable through <i>architectural enforcement</i> "
        "rather than model-level safety constraints. By confining AI to a post-gate advisory role, "
        "LifeLink AI guarantees that no probabilistic output\u2014regardless of model behaviour, "
        "training distribution shift, or inference error\u2014can produce an ABO-incompatible "
        "recommendation. This guarantee is architectural, not probabilistic: the Layer-1 gate is "
        "implemented in a separate Docker container that does not receive AI service outputs as "
        "inputs, making bypass computationally impossible."))
    story.append(s(
        "The logistic regression model\u2019s recall of 75.3% at Brier score 0.2055 confirms "
        "genuine and well-calibrated predictive signal in the three-dimensional RFT feature space. "
        "The AI propensity term contributes 10% to the composite donor score (Eq.\u00a0(6))\u2014"
        "a deliberately modest weight that provides evidence-based uplift without overriding the "
        "clinically more important compatibility and proximity signals. Under the balanced loss "
        "formulation, the model correctly identifies 134 of 178 willing donors, reducing "
        "dispatcher contact with non-responsive individuals and potentially shortening "
        "effective procurement time. The three-level fallback hierarchy ensures that AI "
        "infrastructure failures degrade gracefully to deterministic-only matching at "
        "12.4\u00a0ms mean latency, preserving full emergency operation capability."))
    story.append(s(
        "The deliberate model choice\u2014logistic regression over ensemble methods\u2014warrants "
        "explicit justification in the context of clinical trustworthiness. Preliminary experiments "
        "with random forest and gradient-boosted classifiers yielded marginal ROC-AUC improvements "
        "of 0.00\u20130.01, far below the threshold that would justify the complete loss of "
        "intrinsic interpretability. In an emergency medicine setting, transfusion coordinators "
        "must be able to interrogate and explain any system recommendation to supervising "
        "physicians and hospital ethics committees. Logistic regression achieves this through "
        "its weight vector and sigmoid function\u2014fully transparent to any quantitatively "
        "literate clinician\u2014whereas tree ensembles and neural networks require secondary "
        "approximation methods (SHAP, LIME) that themselves introduce approximation errors [16]."))
    story.append(s(
        "LifeLink AI operationalises the five EU Trustworthy AI properties [13]: "
        "<i>transparency</i>\u2014logistic regression coefficients are directly interpretable "
        "and exposed via an audit API; "
        "<i>non-maleficence</i>\u2014Layer\u00a01 eliminates all incompatible candidates before "
        "any AI computation; "
        "<i>robustness</i>\u2014the three-level fallback hierarchy guarantees continued operation "
        "under AI service failure; "
        "<i>accountability</i>\u2014the immutable inventory_history ledger provides a verifiable "
        "audit trail for every blood unit reserved or dispatched; and "
        "<i>human oversight</i>\u2014final dispatch authority rests with qualified coordinators "
        "or attending clinicians who review ranked candidate lists before any action is taken. "
        "Together, these properties position LifeLink AI as a deployable model for trustworthy "
        "AI integration in high-stakes medical logistics."))

    # ══════════════════════════════════════════════════════════════════════════
    # IX. LIMITATIONS AND ETHICAL CONSIDERATIONS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(sec("IX", "LIMITATIONS AND ETHICAL CONSIDERATIONS"))
    story.append(s(
        "We disclose the following limitations in accordance with responsible AI reporting "
        "principles for healthcare systems [17]. These disclosures are intended to inform "
        "potential clinical partners and regulators about the current implementation boundaries "
        "and the research agenda required before real-world deployment."))

    story.append(bul(
        "<b>Training domain mismatch.</b> The propensity model is trained on the UCI BTSC "
        "benchmark (Hsin-Chu City, Taiwan, 1988\u20131994). Donor behavioural dynamics in "
        "Indian metropolitan populations differ substantially in demographic profile, cultural "
        "motivations (e.g., festival-linked donation campaigns), occupational diversity, and "
        "healthcare access patterns. A model trained on Taiwanese university-area donors from "
        "the late 1980s may not reliably stratify voluntary donors in Bhopal, Mumbai, or "
        "Chennai. Production deployment requires fine-tuning on live operational data collected "
        "during a staged rollout, with periodic retraining as donor population characteristics "
        "evolve."))
    story.append(bul(
        "<b>No live regulatory API validation.</b> When a hospital or blood bank registers "
        "on LifeLink AI, the platform stores its CDSCO or State Blood Transfusion Council "
        "registration number and uploads certificate PDFs. However, the current implementation "
        "does not query live government registration APIs to verify that the supplied "
        "identifiers are current, valid, and not revoked. An administrative governance "
        "review process is required to prevent fraudulent facility onboarding. Automated "
        "API validation against CDSCO/SBTC registries is identified as a high-priority "
        "future engineering task."))
    story.append(bul(
        "<b>Self-reported geolocation accuracy.</b> Donor and facility geolocation coordinates "
        "are derived from postal pin code geocoding at registration time, rather than from "
        "real-time GPS telemetry. In densely populated Indian urban areas, pin codes can "
        "cover areas of 5\u201310\u00a0km\u00b2, introducing proximity score estimation "
        "errors of up to 5\u00a0km relative to actual travel distance. For large-radius "
        "searches (R_search = 100\u00a0km), this error is negligible; for close-range "
        "(R_search = 15\u00a0km), it may meaningfully affect the P_geo ranking signal."))
    story.append(bul(
        "<b>Binary donor availability model.</b> The current availability model represents "
        "donor willingness as a binary flag (available/not available) that the donor sets "
        "via the mobile application. This is a coarse representation: a donor may be "
        "technically \u2018available\u2019 but unavailable to travel to a specific facility "
        "due to transportation constraints, shift work, or family obligations at the time "
        "of the emergency alert. Replacing the binary flag with a temporal probability model "
        "incorporating commuting patterns and historical response data is a priority for "
        "future iterations."))
    story.append(bul(
        "<b>Prototype status and absence of prospective clinical validation.</b> LifeLink AI "
        "is a research prototype evaluated through offline ML cross-validation and automated "
        "software integration tests. It has not undergone prospective randomised controlled "
        "trials in active trauma centres, parallel deployment studies comparing time-to-transfusion "
        "against standard telephonic coordination, or regulatory conformity assessment. "
        "All performance claims are engineering-grade. Formal clinical validation through "
        "IRB-approved prospective implementation studies, and regulatory clearance under the "
        "applicable medical device framework, are non-negotiable prerequisites for deployment "
        "in active emergency medical systems."))

    story.append(s(
        "<b>Ethical Design Principles.</b> LifeLink AI is designed with several explicit ethical "
        "commitments. All dispatch recommendations are presented as ranked advisory lists "
        "to qualified emergency coordinators or attending clinicians, who retain full authority "
        "to override algorithmic ordering based on clinical judgment, direct communication "
        "with donors, or institutional protocols. The system generates no autonomous dispatch "
        "actions. Patient identification on public-facing emergency tracking URLs is protected "
        "by cryptographic UUID tokens derived from request identifiers, preventing casual "
        "de-anonymisation of patient health emergencies from URL inspection. The immutable "
        "inventory audit ledger ensures that every blood unit reservation, release, and "
        "dispatch event is traceable to a specific user account, timestamp, and justification "
        "record\u2014providing full accountability for regulatory and medicolegal review."))

    # ══════════════════════════════════════════════════════════════════════════
    # X. CONCLUSION AND FUTURE WORK
    # ══════════════════════════════════════════════════════════════════════════
    story.append(sec("X", "CONCLUSION AND FUTURE WORK"))
    story.append(s(
        "This paper presented LifeLink AI, a trustworthy hybrid clinical decision-support "
        "architecture for real-time emergency blood matching within the paradigm of Digital "
        "and Precise Medicine. The system addresses a well-documented and high-mortality "
        "failure mode in emergency healthcare logistics: the absence of automated, "
        "real-time, immunohematologically safe coordination between voluntary donors, "
        "licensed blood banks, and hospital emergency coordinators under acute temporal "
        "constraints."))
    story.append(s(
        "The central and novel contribution of this work is the formally defined "
        "<b>two-layer safety contract</b>: an architecturally enforced boundary that "
        "confines deterministic immunohematological and statutory eligibility logic to "
        "Layer\u00a01, and calibrated AI donor response propensity scoring to Layer\u00a02, "
        "with no data flow path by which a Layer-2 AI output can influence a Layer-1 "
        "safety decision. This guarantee is architectural rather than probabilistic, "
        "making it independent of model performance degradation, distribution shift, "
        "or adversarial inputs. The pattern establishes a blueprint for safe AI integration "
        "in other high-stakes medical logistics domains where probabilistic models must "
        "coexist with non-negotiable deterministic safety invariants."))
    story.append(s(
        "The calibrated logistic regression propensity model achieves "
        "ROC-AUC\u202f=\u202f0.7521, Recall\u202f=\u202f0.7528, and "
        "Brier Score\u202f=\u202f0.2055 on the UCI BTSC benchmark under 5-fold stratified "
        "CV, confirming genuine and well-calibrated discriminative signal in the three-dimensional "
        "RFT feature space. The containerised multi-service platform passes 56 automated "
        "integration tests at 100% pass rate, with matching pipeline latencies of "
        "47.2\u00a0ms (AI path, 95th pctl: 83.1\u00a0ms) and 12.4\u00a0ms (deterministic "
        "fallback, 95th pctl: 21.8\u00a0ms)\u2014both well within the sub-second emergency "
        "dispatch budget."))
    story.append(s("<b>Future Research Priorities:</b> The most significant near-term directions are: "
                   "(i)\u00a0<i>Domain-adapted continual learning</i>\u2014online retraining of the "
                   "propensity model on live LifeLink AI donor response telemetry using "
                   "privacy-preserving federated optimisation across multiple deployment regions; "
                   "(ii)\u00a0<i>Learning-to-Rank formulation</i>\u2014replacing heuristic weight "
                   "vectors with LambdaMART or neural ranking models trained on historical "
                   "emergency outcome sequences (whether contacted donors actually responded and "
                   "donated), optimising normalised discounted cumulative gain (NDCG) on the "
                   "ranked dispatch list; "
                   "(iii)\u00a0<i>FHIR\u00a0R4 interoperability</i>\u2014integrating with hospital "
                   "EHR systems via HL7 FHIR R4 APIs to ingest blood type data from patient "
                   "records automatically and cross-reference facility licenses against CDSCO/SBTC "
                   "registries in real time; "
                   "(iv)\u00a0<i>Push notification dispatch</i>\u2014integrating Firebase Cloud "
                   "Messaging for automated, geofenced donor alerts with real-time response "
                   "tracking; and "
                   "(v)\u00a0<i>Prospective clinical validation</i>\u2014IRB-approved implementation "
                   "study in regional trauma centres measuring primary endpoint of time-to-transfusion "
                   "reduction against standard telephonic coordination baselines.", False))

    # ══════════════════════════════════════════════════════════════════════════
    # REFERENCES
    # ══════════════════════════════════════════════════════════════════════════
    story.append(FrameBreak())
    story.append(Paragraph("REFERENCES", SEC))
    story.append(sp(2))

    refs = [
        "[1] B.\u00a0A. Cotton et al., \u201cPrehospital transfusion of plasma and red blood cells in trauma patients,\u201d <i>New England Journal of Medicine</i>, vol.\u00a0379, no.\u00a04, pp.\u00a0315\u2013326, 2018.",
        "[2] D.\u00a0J. Cole and J.\u00a0N. Nance, \u201cTrauma-induced coagulopathy and the golden hour of resuscitation,\u201d <i>Anesthesia & Analgesia</i>, vol.\u00a0129, no.\u00a04, pp.\u00a0912\u2013920, 2019.",
        "[3] World Health Organization, \u201cBlood Safety and Availability,\u201d WHO Fact Sheet, Geneva, 2022.",
        "[4] National Blood Transfusion Council, \u201cAnnual Report on Blood Transfusion Services in India,\u201d Ministry of Health and Family Welfare, New Delhi, 2022.",
        "[5] B. Stanger et al., \u201cBlood inventory management: Discarding practices and optimisation opportunities,\u201d <i>Transfusion Medicine</i>, vol.\u00a022, no.\u00a04, pp.\u00a0248\u2013256, 2012.",
        "[6] E.\u00a0A. Heitmiller et al., \u201cBlood utilisation review: Computerised blood ordering system,\u201d <i>Transfusion</i>, vol.\u00a048, no.\u00a09, pp.\u00a01879\u20131885, 2008.",
        "[7] S.\u00a0S. Roy et al., \u201cIoT and RFID-enabled cold-chain monitoring for perishable healthcare inventory,\u201d <i>IEEE Internet of Things J.</i>, vol.\u00a08, no.\u00a012, pp.\u00a09812\u20139821, 2021.",
        "[8] Ministry of Health and Family Welfare, \u201ce-Rakt Kosh: National Web-based Blood Bank Management System,\u201d MOHFW, New Delhi, 2020.",
        "[9] I.-C. Yeh, K.-J. Yang, and T.-M. Ting, \u201cKnowledge discovery on RFM model using Bernoulli sequence,\u201d <i>Expert Systems with Applications</i>, vol.\u00a036, no.\u00a03, pp.\u00a05866\u20135871, 2009.",
        "[10] C.\u00a0L. Gilliss et al., \u201cPredicting first-time blood donor retention,\u201d <i>Transfusion Medicine</i>, vol.\u00a031, no.\u00a02, pp.\u00a0112\u2013120, 2021.",
        "[11] B. Baesens et al., \u201cUsing neural network rule extraction and decision tables for credit-risk evaluation,\u201d <i>Management Science</i>, vol.\u00a049, no.\u00a03, pp.\u00a0312\u2013329, 2003.",
        "[12] C. Rudin, \u201cStop explaining black box machine learning models for high stakes decisions,\u201d <i>Nature Machine Intelligence</i>, vol.\u00a01, no.\u00a05, pp.\u00a0206\u2013215, 2019.",
        "[13] High-Level Expert Group on AI, \u201cEthics Guidelines for Trustworthy AI,\u201d European Commission, Brussels, 2019.",
        "[14] IEEE Global Initiative on Ethics of Autonomous and Intelligent Systems, \u201cEthically Aligned Design,\u201d IEEE, Piscataway, NJ, 2019.",
        "[15] European Commission, \u201cProposal for a Regulation\u2026 (Artificial Intelligence Act),\u201d COM(2021) 206 final, Brussels, 2021.",
        "[16] F. Doshi-Velez and B. Kim, \u201cTowards a rigorous science of interpretable machine learning,\u201d arXiv:1702.08608, 2017.",
        "[17] J. Amann et al., \u201cExplainability for AI in healthcare: A multidisciplinary perspective,\u201d <i>BMC Medical Informatics and Decision Making</i>, vol.\u00a020, no.\u00a01, p.\u00a0310, 2020.",
        "[18] K. Ramachandran et al., \u201cAlgorithmic decision-support in emergency logistics: A review of safety constraints,\u201d <i>J. Medical Systems</i>, vol.\u00a045, no.\u00a08, p.\u00a078, 2021.",
        "[19] D.\u00a0G. Le Couteur et al., \u201cClinical governance and safety architectures in emergency medical systems,\u201d <i>Lancet Digital Health</i>, vol.\u00a03, no.\u00a05, pp.\u00a0e280\u2013e288, 2021.",
        "[20] A.\u00a0R. Simon et al., \u201cBlood supply chain management: A systematic review,\u201d <i>Vox Sanguinis</i>, vol.\u00a0117, no.\u00a04, pp.\u00a0421\u2013434, 2022.",
    ]
    for i, ref in enumerate(refs):
        if i == 10:
            story.append(FrameBreak())
        story.append(Paragraph(ref, REF))

    # ── Build ──────────────────────────────────────────────────────────────────
    doc = Doc(
        str(PDF_PATH), pagesize=letter,
        leftMargin=MARGIN_L, rightMargin=MARGIN_R,
        topMargin=MARGIN_T, bottomMargin=MARGIN_B,
        title="LifeLink AI: A Trustworthy Hybrid Clinical Decision-Support Architecture "
              "for Real-Time Emergency Blood Matching in Digital and Precise Medicine",
        author="Shivang Mishra, Lakshya Sahu, Kushagra Bhargava, Anshul, Archisha Nigam, Mokshi Jain",
        subject="IEEE MedAI 2026 Regular Research Paper — Area 3: Digital and Precise Medicine"
    )
    doc.build(story)
    print(f"[OK] PDF built: {PDF_PATH}")


build()

# ── Quality Audit ─────────────────────────────────────────────────────────────
import re
reader = pypdf.PdfReader(str(PDF_PATH))
pages  = len(reader.pages)
print(f"\n=== Quality Audit ===")
print(f"Total Pages: {pages}")
print(f"File Size:   {PDF_PATH.stat().st_size:,} bytes")

all_text = ""
entity_err = []
tag_err    = []
email_err  = []

for i, pg in enumerate(reader.pages):
    txt = pg.extract_text() or ""
    all_text += txt
    if bad := re.findall(r"&[a-zA-Z0-9_#]+;", txt):
        entity_err += [(i+1,e) for e in bad]
    if bad := re.findall(r"<[a-zA-Z/][^>]*>", txt):
        tag_err    += [(i+1,t) for t in bad]
    if bad := re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", txt):
        email_err  += [(i+1,e) for e in bad]

print("[PASSED]" if not entity_err else f"[FAILED] {len(entity_err)} HTML entities")
print("[PASSED]" if not tag_err    else f"[FAILED] {len(tag_err)} HTML tags")
print("[PASSED]" if not email_err  else f"[FAILED] {len(email_err)} email addresses")
print(f"Words (approx): {len(all_text.split())}")
if pages <= 12:
    print(f"[PASSED] Page count {pages} \u2264 12")
else:
    print(f"[WARNING] Page count {pages} > 12 — needs content trimming")

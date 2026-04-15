import streamlit as st
import pdfplumber
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from io import BytesIO
import time

st.set_page_config(
    page_title="ResumeIQ — AI Resume Scanner",
    page_icon="⚡",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #f0f2f8;
    min-height: 100vh;
}

/* ── navbar ── */
.navbar {
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(99,102,241,0.1);
    padding: 1rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 2rem;
    border-radius: 0 0 20px 20px;
    box-shadow: 0 4px 20px rgba(99,102,241,0.08);
}

.nav-logo {
    font-size: 1.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.nav-badge {
    background: rgba(99,102,241,0.1);
    border: 1px solid rgba(99,102,241,0.2);
    color: #4f46e5;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 3px 12px;
    border-radius: 20px;
    letter-spacing: 0.08em;
}

/* ── hero ── */
.hero-wrap {
    text-align: center;
    padding: 1rem 1rem 2rem;
}

.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    color: #1e1b4b;
    line-height: 1.2;
    margin-bottom: 0.6rem;
}

.hero-title span {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-sub {
    font-size: 1rem;
    color: #6b7280;
    max-width: 500px;
    margin: 0 auto;
    line-height: 1.7;
}

/* ── glass card ── */
.glass-card {
    background: rgba(255,255,255,0.75);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.9);
    border-radius: 24px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.4rem;
    box-shadow: 0 4px 24px rgba(99,102,241,0.07),
                0 1px 4px rgba(0,0,0,0.04);
}

.card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 1.4rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(99,102,241,0.08);
}

.card-icon {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}

.icon-indigo { background: #eef2ff; border: 1px solid #c7d2fe; }
.icon-purple { background: #f5f3ff; border: 1px solid #ddd6fe; }
.icon-green  { background: #ecfdf5; border: 1px solid #a7f3d0; }
.icon-amber  { background: #fffbeb; border: 1px solid #fde68a; }
.icon-pink   { background: #fdf2f8; border: 1px solid #f9a8d4; }

.card-title {
    font-size: 1rem;
    font-weight: 700;
    color: #1e1b4b;
    margin: 0;
}

.card-subtitle {
    font-size: 0.78rem;
    color: #9ca3af;
    margin: 2px 0 0;
}

/* ── input section ── */
.input-section {
    background: #ffffff;
    border-radius: 24px;
    padding: 2rem;
    margin-bottom: 1.4rem;
    box-shadow: 0 4px 24px rgba(99,102,241,0.07),
                0 1px 4px rgba(0,0,0,0.04);
    border: 1px solid rgba(99,102,241,0.1);
}

.input-section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1e1b4b;
    margin: 0 0 0.3rem;
}

.input-section-sub {
    font-size: 0.82rem;
    color: #9ca3af;
    margin: 0 0 1.5rem;
}

.step-indicator {
    display: flex;
    gap: 8px;
    align-items: center;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}

.step-dot {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    font-size: 0.72rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.step-text {
    font-size: 0.82rem;
    font-weight: 600;
    color: #4b5563;
}

.step-line {
    flex: 1;
    height: 1px;
    background: #e5e7eb;
    min-width: 20px;
}

/* ── stats grid ── */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 1.4rem;
}

.stat-card {
    background: #ffffff;
    border: 1px solid rgba(99,102,241,0.12);
    border-radius: 18px;
    padding: 1.2rem 1rem;
    text-align: center;
    box-shadow: 0 2px 12px rgba(99,102,241,0.06);
}

.stat-number {
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 4px;
}

.num-indigo { color: #4f46e5; }
.num-purple { color: #7c3aed; }
.num-green  { color: #059669; }
.num-amber  { color: #d97706; }

.stat-label {
    font-size: 0.7rem;
    color: #9ca3af;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── score display ── */
.score-display {
    text-align: center;
    padding: 1.5rem 0 1rem;
}

.score-big {
    font-size: 5rem;
    font-weight: 800;
    line-height: 1;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.score-status {
    display: inline-block;
    padding: 5px 18px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    margin-top: 10px;
}

.status-strong {
    background: #ecfdf5;
    color: #065f46;
    border: 1px solid #a7f3d0;
}

.status-partial {
    background: #fffbeb;
    color: #92400e;
    border: 1px solid #fde68a;
}

.status-low {
    background: #fef2f2;
    color: #991b1b;
    border: 1px solid #fecaca;
}

/* ── progress bars ── */
.progress-wrap {
    margin: 0.6rem 0 1rem;
}

.progress-label {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
}

.progress-name {
    font-size: 0.85rem;
    font-weight: 600;
    color: #374151;
}

.progress-val {
    font-size: 0.85rem;
    font-weight: 700;
    color: #4f46e5;
}

.progress-track {
    height: 10px;
    background: #f3f4f6;
    border-radius: 10px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    border-radius: 10px;
    background: linear-gradient(90deg, #4f46e5, #7c3aed);
}

/* ── keyword pills ── */
.pills-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 0.6rem;
}

.pill {
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
}

.pill-found {
    background: #ecfdf5;
    color: #065f46;
    border: 1px solid #6ee7b7;
}

.pill-missing {
    background: #fef2f2;
    color: #991b1b;
    border: 1px solid #fca5a5;
}

/* ── suggestions ── */
.suggestion-item {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    padding: 1rem 1.1rem;
    background: #f9fafb;
    border-radius: 14px;
    margin-bottom: 0.8rem;
    border: 1px solid #f3f4f6;
}

.suggestion-num {
    width: 26px;
    height: 26px;
    border-radius: 8px;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    font-size: 0.72rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 1px;
}

.suggestion-text {
    font-size: 0.9rem;
    color: #374151;
    line-height: 1.6;
}

/* ── section label ── */
.section-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 10px;
}

.label-green { color: #059669; }
.label-red   { color: #dc2626; }

/* ── divider ── */
.soft-divider {
    height: 1px;
    background: #f3f4f6;
    margin: 1.2rem 0;
}

/* ── loading bar ── */
.loading-wrap {
    background: #ffffff;
    border-radius: 20px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.4rem;
    border: 1px solid rgba(99,102,241,0.1);
    box-shadow: 0 4px 24px rgba(99,102,241,0.07);
    text-align: center;
}

.loading-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #1e1b4b;
    margin-bottom: 0.4rem;
}

.loading-sub {
    font-size: 0.8rem;
    color: #9ca3af;
    margin-bottom: 1rem;
}

.loading-track {
    height: 6px;
    background: #f3f4f6;
    border-radius: 10px;
    overflow: hidden;
}

.loading-fill {
    height: 100%;
    border-radius: 10px;
    background: linear-gradient(90deg, #4f46e5, #7c3aed, #ec4899);
    animation: loadSlide 1.8s ease infinite;
}

@keyframes loadSlide {
    0%   { width: 0%;   margin-left: 0%; }
    50%  { width: 60%;  margin-left: 20%; }
    100% { width: 0%;   margin-left: 100%; }
}

/* ── streamlit overrides ── */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.8rem 1.5rem !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 4px 20px rgba(79,70,229,0.35) !important;
    transition: all 0.25s ease !important;
    width: 100% !important;
}

.stButton > button:hover {
    box-shadow: 0 6px 28px rgba(79,70,229,0.5) !important;
    transform: translateY(-2px) !important;
}

.stDownloadButton > button {
    background: linear-gradient(135deg, #059669, #0891b2) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.75rem 1.5rem !important;
    box-shadow: 0 4px 16px rgba(5,150,105,0.3) !important;
    width: 100% !important;
}

/* solid white inputs */
.stTextArea textarea {
    background: #ffffff !important;
    border: 1.5px solid #e5e7eb !important;
    border-radius: 14px !important;
    color: #111827 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
    line-height: 1.6 !important;
    padding: 12px 14px !important;
}

.stTextArea textarea:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.1) !important;
}

.stTextArea textarea::placeholder {
    color: #9ca3af !important;
}

.stTextInput input {
    background: #ffffff !important;
    border: 1.5px solid #e5e7eb !important;
    border-radius: 14px !important;
    color: #111827 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
    padding: 10px 14px !important;
}

.stTextInput input:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.1) !important;
}

.stTextInput input::placeholder {
    color: #9ca3af !important;
}

div[data-testid="stFileUploader"] {
    background: #ffffff !important;
    border: 2px dashed #c7d2fe !important;
    border-radius: 16px !important;
    padding: 0.5rem !important;
}

div[data-testid="stFileUploader"]:hover {
    border-color: #4f46e5 !important;
    background: #eef2ff !important;
}

label, .stTextArea label, .stTextInput label,
div[data-testid="stFileUploader"] label {
    color: #374151 !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
}

.stSuccess {
    background: #ecfdf5 !important;
    color: #065f46 !important;
    border: 1px solid #a7f3d0 !important;
    border-radius: 12px !important;
}

.stWarning {
    background: #fffbeb !important;
    color: #92400e !important;
    border: 1px solid #fde68a !important;
    border-radius: 12px !important;
}

.stInfo {
    background: #eef2ff !important;
    color: #3730a3 !important;
    border: 1px solid #c7d2fe !important;
    border-radius: 12px !important;
}

#MainMenu {visibility: hidden;}
footer   {visibility: hidden;}
header   {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── keywords ──────────────────────────────────────────────────
SKILL_KEYWORDS = [
    "python", "javascript", "java", "typescript", "react", "angular", "vue",
    "node", "sql", "nosql", "mongodb", "postgresql", "mysql", "aws", "azure",
    "gcp", "docker", "kubernetes", "git", "rest", "api", "graphql",
    "machine learning", "deep learning", "nlp", "tensorflow", "pytorch",
    "pandas", "numpy", "scikit", "html", "css", "c++", "c#", "linux",
    "tableau", "power bi", "figma", "excel", "automation", "ai", "devops"
]

EXPERIENCE_KEYWORDS = [
    "developed", "managed", "led", "built", "designed", "implemented",
    "delivered", "improved", "increased", "reduced", "collaborated",
    "deployed", "maintained", "created", "optimized", "analyzed",
    "architected", "launched", "spearheaded", "mentored", "coordinated"
]

EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "degree", "engineering", "computer science",
    "information technology", "b.tech", "m.tech", "mba", "certification",
    "certified", "diploma", "graduate", "university", "college", "gpa"
]

SUGGESTION_RULES = {
    "action verbs": {
        "check": ["developed", "managed", "led", "built", "designed",
                  "implemented", "delivered", "improved", "optimized"],
        "tip": "Add strong action verbs like Developed, Led, Optimized at the start of your bullet points."
    },
    "quantified results": {
        "check": ["%", "increased", "reduced", "improved", "saved", "grew"],
        "tip": "Add numbers and metrics. Example: Improved performance by 30% or Managed a team of 5 engineers."
    },
    "technical skills section": {
        "check": ["skills", "technologies", "tools", "proficient", "expertise"],
        "tip": "Add a dedicated Skills section clearly listing your tools and technologies."
    },
    "education details": {
        "check": ["gpa", "cgpa", "grade", "graduated", "degree"],
        "tip": "Include your GPA, graduation year, and full degree name in your Education section."
    },
    "certifications": {
        "check": ["certified", "certification", "certificate"],
        "tip": "Add relevant certifications. AWS, Google Cloud or Azure certifications greatly boost your profile."
    },
    "contact information": {
        "check": ["linkedin", "github", "portfolio", "email", "phone"],
        "tip": "Include LinkedIn, GitHub, email and phone number at the top of your resume."
    },
    "summary section": {
        "check": ["summary", "objective", "profile", "about"],
        "tip": "Add a 2-3 line professional summary at the top highlighting your experience and goals."
    },
    "project details": {
        "check": ["project", "projects", "built", "developed", "created"],
        "tip": "Include a Projects section with 2-3 strong projects, tech stack used, and the problem they solve."
    }
}

# ── helpers ───────────────────────────────────────────────────
def extract_text_from_pdf(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        return " ".join(page.extract_text() or "" for page in pdf.pages)

def get_matches(text, keyword_list):
    text_lower = text.lower()
    matched = {kw for kw in keyword_list if kw in text_lower}
    missing = {kw for kw in keyword_list if kw not in text_lower}
    return matched, missing

def calc_score(matched, total):
    return round(len(matched) / len(total) * 100) if total else 0

def get_status(score):
    if score >= 70:
        return '<span class="score-status status-strong">⚡ Strong Match</span>'
    elif score >= 40:
        return '<span class="score-status status-partial">⚠️ Partial Match</span>'
    else:
        return '<span class="score-status status-low">❌ Needs Work</span>'

def get_smart_suggestions(resume_text, missing_skills):
    suggestions = []
    resume_lower = resume_text.lower()
    for rule_name, rule in SUGGESTION_RULES.items():
        found = any(word in resume_lower for word in rule["check"])
        if not found:
            suggestions.append(rule["tip"])
    if missing_skills:
        top_missing = list(missing_skills)[:5]
        suggestions.append(
            f"Add these missing keywords: {', '.join(top_missing)} "
            f"— they appear in the job description but not in your resume."
        )
    if not suggestions:
        suggestions.append(
            "Great job! Your resume covers most important areas. "
            "Consider tailoring your summary specifically for this role."
        )
    return suggestions[:6]

def animated_progress(label, value):
    st.markdown(f"""
    <div class="progress-wrap">
        <div class="progress-label">
            <span class="progress-name">{label}</span>
            <span class="progress-val">{value}%</span>
        </div>
        <div class="progress-track">
            <div class="progress-fill" style="width:{value}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def generate_pdf(resume_name, overall_score, skill_score, exp_score,
                 edu_score, matched_skills, missing_skills, suggestions, password):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=inch*0.75, leftMargin=inch*0.75,
                            topMargin=inch*0.75, bottomMargin=inch*0.75)
    styles = getSampleStyleSheet()
    story  = []

    title_style = ParagraphStyle(
        'Title', parent=styles['Title'],
        fontSize=22, textColor=colors.HexColor('#4f46e5'), spaceAfter=4)
    sub_style = ParagraphStyle(
        'Sub', parent=styles['Normal'],
        fontSize=10, textColor=colors.HexColor('#6b7280'), spaceAfter=16)
    heading_style = ParagraphStyle(
        'Heading', parent=styles['Heading2'],
        fontSize=13, textColor=colors.HexColor('#1e1b4b'),
        spaceBefore=14, spaceAfter=6)
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontSize=10, leading=16, textColor=colors.HexColor('#374151'))

    story.append(Paragraph("ResumeIQ — AI Scan Report", title_style))
    story.append(Paragraph(f"Resume analysed: {resume_name}", sub_style))

    story.append(Paragraph("Score Breakdown", heading_style))
    score_data = [
        ["Category", "Score", "Rating"],
        ["Overall Match", f"{overall_score}%",
         "Strong" if overall_score >= 70 else
         "Partial" if overall_score >= 40 else "Low"],
        ["Skills",     f"{skill_score}%",
         "Strong" if skill_score >= 70 else
         "Partial" if skill_score >= 40 else "Low"],
        ["Experience", f"{exp_score}%",
         "Strong" if exp_score >= 70 else
         "Partial" if exp_score >= 40 else "Low"],
        ["Education",  f"{edu_score}%",
         "Strong" if edu_score >= 70 else
         "Partial" if edu_score >= 40 else "Low"],
    ]
    tbl = Table(score_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    tbl.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,0), colors.HexColor('#4f46e5')),
        ('TEXTCOLOR',    (0,0), (-1,0), colors.white),
        ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0,0), (-1,-1), 10),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),
         [colors.HexColor('#eef2ff'), colors.white]),
        ('GRID',         (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
        ('PADDING',      (0,0), (-1,-1), 8),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Matched Keywords", heading_style))
    story.append(Paragraph(
        ", ".join(sorted(matched_skills)) if matched_skills else "None found",
        body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Missing Keywords", heading_style))
    story.append(Paragraph(
        ", ".join(sorted(missing_skills)) if missing_skills else "None — great job!",
        body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Improvement Suggestions", heading_style))
    for i, tip in enumerate(suggestions, 1):
        story.append(Paragraph(f"{i}. {tip}", body_style))
        story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ═══════════════════════════════════════════════════════════════
#  PAGE
# ═══════════════════════════════════════════════════════════════

# navbar
st.markdown("""
<div class="navbar">
    <div class="nav-logo">⚡ ResumeIQ</div>
    <div class="nav-badge">AI POWERED · FREE</div>
</div>
""", unsafe_allow_html=True)

# hero
st.markdown("""
<div class="hero-wrap">
    <div class="hero-title">Land your <span>dream job</span><br>with a smarter resume</div>
    <div class="hero-sub">
        Upload your resume · Paste any job description ·
        Get your match score and AI-powered tips instantly
    </div>
</div>
""", unsafe_allow_html=True)

# ── input card ────────────────────────────────────────────────
st.markdown("""
<div class="input-section">
    <div class="input-section-title">📋 Analyze Your Resume</div>
    <div class="input-section-sub">
        Complete all 3 steps below and click Scan
    </div>
    <div class="step-indicator">
        <div class="step-dot">1</div>
        <div class="step-text">Upload Resume</div>
        <div class="step-line"></div>
        <div class="step-dot">2</div>
        <div class="step-text">Paste Job Description</div>
        <div class="step-line"></div>
        <div class="step-dot">3</div>
        <div class="step-text">Scan</div>
    </div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Step 1 — Upload your Resume (PDF only)",
    type=["pdf"]
)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

jd_text = st.text_area(
    "Step 2 — Paste the Job Description",
    height=200,
    placeholder="Copy and paste the full job description here. "
                "The more complete the JD, the better your match score."
)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

pdf_password = st.text_input(
    "Step 3 — Set a password for your PDF report",
    type="password",
    placeholder="Choose a strong password to protect your report"
)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

scan_clicked = st.button("⚡ Scan My Resume", use_container_width=True)

# ── validation ────────────────────────────────────────────────
if scan_clicked:
    if not uploaded_file:
        st.warning("⚠️ Please upload your resume PDF in Step 1.")
    elif not jd_text.strip():
        st.warning("⚠️ Please paste a job description in Step 2.")
    elif not pdf_password.strip():
        st.warning("⚠️ Please set a PDF password in Step 3.")
    else:
        # loading
        loading = st.empty()
        loading.markdown("""
        <div class="loading-wrap">
            <div class="loading-title">✨ Scanning your resume with AI...</div>
            <div class="loading-sub">
                Extracting keywords · Matching skills · Generating insights
            </div>
            <div class="loading-track">
                <div class="loading-fill"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner(""):
            resume_text = extract_text_from_pdf(uploaded_file)
            time.sleep(1.5)

            matched_skills, missing_skills = get_matches(
                resume_text, SKILL_KEYWORDS)
            matched_exp,    missing_exp    = get_matches(
                resume_text, EXPERIENCE_KEYWORDS)
            matched_edu,    missing_edu    = get_matches(
                resume_text, EDUCATION_KEYWORDS)

            all_matched  = matched_skills | matched_exp | matched_edu
            all_keywords = set(
                SKILL_KEYWORDS + EXPERIENCE_KEYWORDS + EDUCATION_KEYWORDS)

            overall  = calc_score(all_matched,    all_keywords)
            skill_sc = calc_score(matched_skills, SKILL_KEYWORDS)
            exp_sc   = calc_score(matched_exp,    EXPERIENCE_KEYWORDS)
            edu_sc   = calc_score(matched_edu,    EDUCATION_KEYWORDS)

            suggestions = get_smart_suggestions(resume_text, missing_skills)

        loading.empty()

        st.success("✅ Scan complete! Here are your results.")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ── stat cards ────────────────────────────────────────
        st.markdown(f"""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number num-indigo">{overall}%</div>
                <div class="stat-label">Overall Match</div>
            </div>
            <div class="stat-card">
                <div class="stat-number num-purple">{skill_sc}%</div>
                <div class="stat-label">Skills Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-number num-green">{len(all_matched)}</div>
                <div class="stat-label">Keywords Found</div>
            </div>
            <div class="stat-card">
                <div class="stat-number num-amber">{len(missing_skills)}</div>
                <div class="stat-label">Skills Missing</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── overall score ─────────────────────────────────────
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-header">
                <div class="card-icon icon-indigo">🎯</div>
                <div>
                    <div class="card-title">Overall Match Score</div>
                    <div class="card-subtitle">
                        Based on full keyword analysis
                    </div>
                </div>
            </div>
            <div class="score-display">
                <div class="score-big" id="score-el">0%</div>
                <div style="margin-top:12px;">{get_status(overall)}</div>
            </div>
        </div>
        <script>
        (function() {{
            var el = document.getElementById('score-el');
            if (!el) return;
            var target = {overall}, cur = 0,
                step = Math.max(1, Math.ceil(target / 50));
            var t = setInterval(function() {{
                cur = Math.min(cur + step, target);
                el.textContent = cur + '%';
                if (cur >= target) clearInterval(t);
            }}, 25);
        }})();
        </script>
        """, unsafe_allow_html=True)

        # ── score breakdown ───────────────────────────────────
        st.markdown("""
        <div class="glass-card">
            <div class="card-header">
                <div class="card-icon icon-purple">📊</div>
                <div>
                    <div class="card-title">Score Breakdown</div>
                    <div class="card-subtitle">By resume category</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        animated_progress("🛠 Skills", skill_sc)
        animated_progress("💼 Experience", exp_sc)
        animated_progress("🎓 Education", edu_sc)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── keyword analysis ──────────────────────────────────
        found_pills = " ".join([
            f'<span class="pill pill-found">{kw}</span>'
            for kw in sorted(all_matched)
        ])
        missing_pills = " ".join([
            f'<span class="pill pill-missing">{kw}</span>'
            for kw in sorted(missing_skills)
        ])

        st.markdown(f"""
        <div class="glass-card">
            <div class="card-header">
                <div class="card-icon icon-green">🔑</div>
                <div>
                    <div class="card-title">Keyword Analysis</div>
                    <div class="card-subtitle">
                        {len(all_matched)} matched · {len(missing_skills)} missing
                    </div>
                </div>
            </div>
            <div style="margin-bottom:1.2rem;">
                <div class="section-label label-green">
                    ✅ Matched Keywords
                </div>
                <div class="pills-wrap">
                    {found_pills if found_pills else
                     '<span style="color:#9ca3af;font-size:0.85rem;">'
                     'None found</span>'}
                </div>
            </div>
            <div class="soft-divider"></div>
            <div style="margin-top:1rem;">
                <div class="section-label label-red">
                    ❌ Missing Keywords
                </div>
                <div class="pills-wrap">
                    {missing_pills if missing_pills else
                     '<span style="color:#059669;font-size:0.85rem;font-weight:600;">'
                     '🎉 None — great job!</span>'}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── suggestions ───────────────────────────────────────
        suggestions_html = "".join([f"""
        <div class="suggestion-item">
            <div class="suggestion-num">{i}</div>
            <div class="suggestion-text">{tip}</div>
        </div>""" for i, tip in enumerate(suggestions, 1)])

        st.markdown(f"""
        <div class="glass-card">
            <div class="card-header">
                <div class="card-icon icon-amber">💡</div>
                <div>
                    <div class="card-title">Smart Improvement Suggestions</div>
                    <div class="card-subtitle">
                        AI-powered tips to strengthen your resume
                    </div>
                </div>
            </div>
            {suggestions_html}
        </div>
        """, unsafe_allow_html=True)

        # ── export ────────────────────────────────────────────
        st.markdown("""
        <div class="glass-card">
            <div class="card-header">
                <div class="card-icon icon-green">📥</div>
                <div>
                    <div class="card-title">Export Your Report</div>
                    <div class="card-subtitle">
                        Download full analysis as a password-protected PDF
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        pdf_buffer = generate_pdf(
            uploaded_file.name, overall, skill_sc, exp_sc, edu_sc,
            all_matched, missing_skills, suggestions, pdf_password
        )
        st.download_button(
            label="⬇️ Download PDF Report",
            data=pdf_buffer,
            file_name="resumeiq_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        st.info(f"🔐 Your PDF password: **{pdf_password}**")
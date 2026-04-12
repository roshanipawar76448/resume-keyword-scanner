import streamlit as st
import pdfplumber
import os
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
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

/* ── hero ── */
.hero-wrap {
    text-align: center;
    padding: 2.5rem 1rem 2rem;
}

.hero-badge {
    display: inline-block;
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(99, 102, 241, 0.3);
    color: #a5b4fc;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 4px 14px;
    border-radius: 20px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.15;
    margin-bottom: 0.6rem;
}

.hero-title span {
    background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-sub {
    font-size: 0.95rem;
    color: #94a3b8;
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ── glass card ── */
.glass-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 24px;
    padding: 1.8rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 1.2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

.card-icon {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}

.card-icon.indigo { background: rgba(99,102,241,0.2); border: 1px solid rgba(99,102,241,0.3); }
.card-icon.purple { background: rgba(168,85,247,0.2); border: 1px solid rgba(168,85,247,0.3); }
.card-icon.pink   { background: rgba(236,72,153,0.2); border: 1px solid rgba(236,72,153,0.3); }
.card-icon.green  { background: rgba(16,185,129,0.2); border: 1px solid rgba(16,185,129,0.3); }
.card-icon.amber  { background: rgba(245,158,11,0.2); border: 1px solid rgba(245,158,11,0.3); }

.card-title {
    font-size: 1rem;
    font-weight: 700;
    color: #f1f5f9;
    margin: 0;
}

.card-subtitle {
    font-size: 0.75rem;
    color: #64748b;
    margin: 2px 0 0;
}

/* ── stat cards ── */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 1.2rem;
}

.stat-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 1.2rem 1rem;
    text-align: center;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
}

.stat-number {
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 4px;
}

.stat-number.indigo { color: #818cf8; }
.stat-number.purple { color: #c084fc; }
.stat-number.green  { color: #34d399; }
.stat-number.amber  { color: #fbbf24; }

.stat-label {
    font-size: 0.7rem;
    color: #64748b;
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
    font-size: 5.5rem;
    font-weight: 800;
    line-height: 1;
    background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
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
    background: rgba(16,185,129,0.15);
    color: #34d399;
    border: 1px solid rgba(16,185,129,0.3);
}

.status-partial {
    background: rgba(245,158,11,0.15);
    color: #fbbf24;
    border: 1px solid rgba(245,158,11,0.3);
}

.status-low {
    background: rgba(239,68,68,0.15);
    color: #f87171;
    border: 1px solid rgba(239,68,68,0.3);
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
    font-size: 0.82rem;
    font-weight: 600;
    color: #cbd5e1;
}

.progress-val {
    font-size: 0.82rem;
    font-weight: 700;
    color: #818cf8;
}

.progress-track {
    height: 8px;
    background: rgba(255,255,255,0.08);
    border-radius: 10px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    border-radius: 10px;
    background: linear-gradient(90deg, #6366f1, #a855f7);
    animation: fillBar 1.2s ease forwards;
}

@keyframes fillBar {
    from { width: 0%; }
    to   { width: var(--target); }
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
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

.pill-found {
    background: rgba(16,185,129,0.15);
    color: #34d399;
    border: 1px solid rgba(16,185,129,0.25);
}

.pill-missing {
    background: rgba(239,68,68,0.12);
    color: #f87171;
    border: 1px solid rgba(239,68,68,0.2);
}

.pill-skill {
    background: rgba(99,102,241,0.15);
    color: #a5b4fc;
    border: 1px solid rgba(99,102,241,0.25);
}

/* ── suggestion items ── */
.suggestion-item {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    padding: 1rem;
    background: rgba(255,255,255,0.04);
    border-radius: 14px;
    margin-bottom: 0.8rem;
    border: 1px solid rgba(255,255,255,0.07);
}

.suggestion-num {
    width: 26px;
    height: 26px;
    border-radius: 8px;
    background: linear-gradient(135deg, #6366f1, #a855f7);
    color: white;
    font-size: 0.72rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.suggestion-text {
    font-size: 0.88rem;
    color: #cbd5e1;
    line-height: 1.6;
}

/* ── score counter animation ── */
.counter-wrap {
    display: flex;
    justify-content: center;
}

/* ── loading bar ── */
.loading-bar-wrap {
    background: rgba(255,255,255,0.05);
    border-radius: 10px;
    height: 6px;
    overflow: hidden;
    margin: 1rem 0;
}

.loading-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
    border-radius: 10px;
    animation: loadingAnim 2s ease infinite;
}

@keyframes loadingAnim {
    0%   { width: 0%; margin-left: 0%; }
    50%  { width: 60%; margin-left: 20%; }
    100% { width: 0%; margin-left: 100%; }
}

/* ── divider ── */
.glass-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.4), transparent);
    margin: 1rem 0;
}

/* ── section label ── */
.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 8px;
}

.label-green  { color: #34d399; }
.label-red    { color: #f87171; }

/* ── streamlit overrides ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #a855f7) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.75rem 1.5rem !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 0 20px rgba(99,102,241,0.4), 0 4px 14px rgba(99,102,241,0.3) !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
}

.stButton > button:hover {
    box-shadow: 0 0 35px rgba(99,102,241,0.6), 0 6px 20px rgba(99,102,241,0.4) !important;
    transform: translateY(-2px) !important;
}

.stDownloadButton > button {
    background: linear-gradient(135deg, #10b981, #0891b2) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    box-shadow: 0 0 20px rgba(16,185,129,0.3) !important;
    width: 100% !important;
}

.stTextArea textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
    color: #f1f5f9 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
}

.stTextArea textarea::placeholder { color: #475569 !important; }

.stTextInput input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
    color: #f1f5f9 !important;
    font-family: 'Inter', sans-serif !important;
}

.stTextInput input::placeholder { color: #475569 !important; }

div[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px dashed rgba(99,102,241,0.4) !important;
    border-radius: 14px !important;
}

label {
    color: #94a3b8 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}

.stSuccess, .stWarning, .stError, .stInfo {
    border-radius: 12px !important;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* score counter JS animation */
.animated-score {
    font-size: 5.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ── keyword categories ─────────────────────────────────────────
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
            f"Add these missing keywords to your resume: "
            f"{', '.join(top_missing)} — they appear in the job description but not in your resume."
        )
    if not suggestions:
        suggestions.append("Great job! Your resume covers most important areas. "
                           "Consider tailoring your summary specifically for this role.")
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
    story = []

    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                  fontSize=20,
                                  textColor=colors.HexColor('#6366f1'),
                                  spaceAfter=6)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'],
                                    fontSize=13,
                                    textColor=colors.HexColor('#111827'),
                                    spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle('Body', parent=styles['Normal'],
                                 fontSize=10, leading=16,
                                 textColor=colors.HexColor('#374151'))

    story.append(Paragraph("ResumeIQ — AI Scan Report", title_style))
    story.append(Paragraph(f"Resume: {resume_name}", body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Score Breakdown", heading_style))
    score_data = [
        ["Category", "Score", "Rating"],
        ["Overall Match", f"{overall_score}%",
         "Strong" if overall_score >= 70 else "Partial" if overall_score >= 40 else "Low"],
        ["Skills", f"{skill_score}%",
         "Strong" if skill_score >= 70 else "Partial" if skill_score >= 40 else "Low"],
        ["Experience", f"{exp_score}%",
         "Strong" if exp_score >= 70 else "Partial" if exp_score >= 40 else "Low"],
        ["Education", f"{edu_score}%",
         "Strong" if edu_score >= 70 else "Partial" if edu_score >= 40 else "Low"],
    ]
    table = Table(score_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.HexColor('#eef2ff'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Matched Keywords", heading_style))
    matched_text = ", ".join(sorted(matched_skills)) if matched_skills else "None found"
    story.append(Paragraph(matched_text, body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Missing Keywords", heading_style))
    missing_text = ", ".join(sorted(missing_skills)) if missing_skills else "None — great job!"
    story.append(Paragraph(missing_text, body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Improvement Suggestions", heading_style))
    for i, tip in enumerate(suggestions, 1):
        story.append(Paragraph(f"{i}. {tip}", body_style))
        story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ── UI ────────────────────────────────────────────────────────

# hero
st.markdown("""
<div class="hero-wrap">
    <div class="hero-badge">⚡ AI Powered · NLP · Free</div>
    <div class="hero-title">Resume<span>IQ</span></div>
    <div class="hero-sub">
        Upload your resume · Match any job description · 
        Get AI-powered insights in seconds
    </div>
</div>
""", unsafe_allow_html=True)

# input card
st.markdown("""
<div class="glass-card">
    <div class="card-header">
        <div class="card-icon indigo">📁</div>
        <div>
            <div class="card-title">Analyze Your Resume</div>
            <div class="card-subtitle">Fill all fields and click Scan</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "📄 Upload Resume (PDF only)", type=["pdf"])

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

jd_text = st.text_area(
    "📋 Paste Job Description",
    height=160,
    placeholder="Copy and paste the full job description here...")

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

pdf_password = st.text_input(
    "🔐 PDF Report Password",
    type="password",
    placeholder="Set a password to protect your PDF report...")

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

scan_clicked = st.button("⚡ Scan My Resume", use_container_width=True)

if scan_clicked:
    if not uploaded_file:
        st.warning("⚠️ Please upload your resume PDF.")
    elif not jd_text.strip():
        st.warning("⚠️ Please paste a job description.")
    elif not pdf_password.strip():
        st.warning("⚠️ Please set a PDF report password.")
    else:
        # loading animation
        st.markdown("""
        <div class="glass-card">
            <div style="text-align:center; padding: 0.5rem 0;">
                <div style="font-size:0.85rem; color:#94a3b8; 
                            font-weight:500; margin-bottom:0.8rem;">
                    ✨ Scanning your resume with AI...
                </div>
                <div class="loading-bar-wrap">
                    <div class="loading-bar-fill"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner(""):
            resume_text = extract_text_from_pdf(uploaded_file)
            time.sleep(1.2)

            matched_skills, missing_skills = get_matches(resume_text, SKILL_KEYWORDS)
            matched_exp,    missing_exp    = get_matches(resume_text, EXPERIENCE_KEYWORDS)
            matched_edu,    missing_edu    = get_matches(resume_text, EDUCATION_KEYWORDS)

            all_matched  = matched_skills | matched_exp | matched_edu
            all_keywords = set(SKILL_KEYWORDS + EXPERIENCE_KEYWORDS + EDUCATION_KEYWORDS)

            overall  = calc_score(all_matched,    all_keywords)
            skill_sc = calc_score(matched_skills, SKILL_KEYWORDS)
            exp_sc   = calc_score(matched_exp,    EXPERIENCE_KEYWORDS)
            edu_sc   = calc_score(matched_edu,    EDUCATION_KEYWORDS)

            suggestions = get_smart_suggestions(resume_text, missing_skills)

        # stat cards
        st.markdown(f"""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number indigo">{overall}%</div>
                <div class="stat-label">Overall Match</div>
            </div>
            <div class="stat-card">
                <div class="stat-number purple">{skill_sc}%</div>
                <div class="stat-label">Skills Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-number green">{len(all_matched)}</div>
                <div class="stat-label">Keywords Found</div>
            </div>
            <div class="stat-card">
                <div class="stat-number amber">{len(missing_skills)}</div>
                <div class="stat-label">Keywords Missing</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # animated score counter
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-header">
                <div class="card-icon indigo">🎯</div>
                <div>
                    <div class="card-title">Overall Match Score</div>
                    <div class="card-subtitle">Based on full keyword analysis</div>
                </div>
            </div>
            <div class="score-display">
                <div class="animated-score" id="score-counter">0%</div>
                <div style="margin-top:12px;">{get_status(overall)}</div>
            </div>
        </div>
        <script>
            function animateCounter(target) {{
                var el = document.getElementById('score-counter');
                if (!el) return;
                var current = 0;
                var step = Math.ceil(target / 40);
                var timer = setInterval(function() {{
                    current += step;
                    if (current >= target) {{
                        current = target;
                        clearInterval(timer);
                    }}
                    el.textContent = current + '%';
                }}, 30);
            }}
            setTimeout(function() {{ animateCounter({overall}); }}, 300);
        </script>
        """, unsafe_allow_html=True)

        # score breakdown
        st.markdown("""
        <div class="glass-card">
            <div class="card-header">
                <div class="card-icon purple">📊</div>
                <div>
                    <div class="card-title">Score Breakdown</div>
                    <div class="card-subtitle">By resume category</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        animated_progress("🛠 Skills", skill_sc)
        animated_progress("💼 Experience", exp_sc)
        animated_progress("🎓 Education", edu_sc)
        st.markdown('</div>', unsafe_allow_html=True)

        # keywords
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
                <div class="card-icon green">🔑</div>
                <div>
                    <div class="card-title">Keyword Analysis</div>
                    <div class="card-subtitle">
                        {len(all_matched)} matched · {len(missing_skills)} missing
                    </div>
                </div>
            </div>
            <div style="margin-bottom:1.2rem;">
                <div class="section-label label-green">✅ Matched Keywords</div>
                <div class="pills-wrap">
                    {found_pills if found_pills else
                     '<span style="color:#475569;font-size:0.82rem;">None found</span>'}
                </div>
            </div>
            <div class="glass-divider"></div>
            <div style="margin-top:1rem;">
                <div class="section-label label-red">❌ Missing Keywords</div>
                <div class="pills-wrap">
                    {missing_pills if missing_pills else
                     '<span style="color:#34d399;font-size:0.82rem;">None — great job!</span>'}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # suggestions
        suggestions_html = ""
        for i, tip in enumerate(suggestions, 1):
            suggestions_html += f"""
            <div class="suggestion-item">
                <div class="suggestion-num">{i}</div>
                <div class="suggestion-text">{tip}</div>
            </div>"""

        st.markdown(f"""
        <div class="glass-card">
            <div class="card-header">
                <div class="card-icon amber">💡</div>
                <div>
                    <div class="card-title">Smart Suggestions</div>
                    <div class="card-subtitle">
                        AI-powered tips to improve your resume
                    </div>
                </div>
            </div>
            {suggestions_html}
        </div>
        """, unsafe_allow_html=True)

        # export
        st.markdown("""
        <div class="glass-card">
            <div class="card-header">
                <div class="card-icon green">📥</div>
                <div>
                    <div class="card-title">Export Your Report</div>
                    <div class="card-subtitle">
                        Download full analysis as PDF
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
        st.info(f"🔐 PDF Password: **{pdf_password}**")
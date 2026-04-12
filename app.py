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

# ── page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeIQ — Smart Resume Scanner",
    page_icon="⚡",
    layout="wide"
)

# ── custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #f7f8fc;
}

/* ── sidebar ── */
section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e8eaf0;
    padding-top: 1rem;
}

section[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1.2rem;
}

.sidebar-logo {
    font-size: 1.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}

.sidebar-tagline {
    font-size: 0.78rem;
    color: #6b7280;
    margin-bottom: 1.8rem;
    font-weight: 400;
}

.sidebar-section {
    font-size: 0.7rem;
    font-weight: 700;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 1.2rem 0 0.5rem;
}

/* ── main area ── */
.main-hero {
    padding: 2rem 0 1.5rem;
    border-bottom: 1px solid #e8eaf0;
    margin-bottom: 2rem;
}

.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #111827;
    margin: 0 0 0.4rem;
    line-height: 1.2;
}

.hero-title span {
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-sub {
    font-size: 0.95rem;
    color: #6b7280;
    font-weight: 400;
    margin: 0;
}

/* ── stat cards ── */
.stats-row {
    display: flex;
    gap: 16px;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}

.stat-card {
    flex: 1;
    min-width: 140px;
    background: #ffffff;
    border: 1px solid #e8eaf0;
    border-radius: 16px;
    padding: 1.2rem 1rem;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

.stat-number {
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 4px;
}

.stat-number.blue { color: #2563eb; }
.stat-number.purple { color: #7c3aed; }
.stat-number.green { color: #059669; }
.stat-number.orange { color: #d97706; }

.stat-label {
    font-size: 0.75rem;
    color: #9ca3af;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── section cards ── */
.section-card {
    background: #ffffff;
    border: 1px solid #e8eaf0;
    border-radius: 20px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.4rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

.card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1.2rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid #f3f4f6;
}

.card-icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
}

.card-icon.blue { background: #eff6ff; }
.card-icon.purple { background: #f5f3ff; }
.card-icon.green { background: #ecfdf5; }
.card-icon.orange { background: #fffbeb; }

.card-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #111827;
    margin: 0;
}

.card-subtitle {
    font-size: 0.78rem;
    color: #9ca3af;
    margin: 0;
}

/* ── score display ── */
.score-display {
    text-align: center;
    padding: 1rem 0;
}

.score-big {
    font-size: 5rem;
    font-weight: 800;
    line-height: 1;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.score-status {
    display: inline-block;
    padding: 4px 16px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    margin-top: 8px;
}

.status-strong {
    background: #ecfdf5;
    color: #059669;
    border: 1px solid #a7f3d0;
}

.status-partial {
    background: #fffbeb;
    color: #d97706;
    border: 1px solid #fde68a;
}

.status-low {
    background: #fef2f2;
    color: #dc2626;
    border: 1px solid #fecaca;
}

/* ── keyword pills ── */
.pills-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 0.5rem;
}

.pill {
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 500;
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

/* ── suggestion items ── */
.suggestion-item {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    padding: 0.9rem 1rem;
    background: #f9fafb;
    border-radius: 12px;
    margin-bottom: 0.7rem;
    border: 1px solid #f3f4f6;
}

.suggestion-num {
    width: 24px;
    height: 24px;
    border-radius: 8px;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
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
    font-size: 0.88rem;
    color: #374151;
    line-height: 1.6;
}

/* ── progress bar animation ── */
.progress-wrap {
    margin: 0.5rem 0 1rem;
}

.progress-label {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
}

.progress-name {
    font-size: 0.82rem;
    font-weight: 600;
    color: #374151;
}

.progress-val {
    font-size: 0.82rem;
    font-weight: 700;
    color: #2563eb;
}

.progress-track {
    height: 8px;
    background: #f3f4f6;
    border-radius: 10px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    border-radius: 10px;
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    transition: width 1s ease;
}

/* ── empty state ── */
.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    color: #9ca3af;
}

.empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.empty-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #6b7280;
    margin-bottom: 0.4rem;
}

.empty-sub {
    font-size: 0.85rem;
    color: #9ca3af;
}

/* ── streamlit overrides ── */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.65rem 1.5rem !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 14px rgba(37,99,235,0.3) !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}

.stButton > button:hover {
    box-shadow: 0 6px 20px rgba(37,99,235,0.45) !important;
    transform: translateY(-1px) !important;
}

.stDownloadButton > button {
    background: linear-gradient(135deg, #059669, #0891b2) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 14px rgba(5,150,105,0.3) !important;
    width: 100% !important;
}

.stTextArea textarea {
    border-radius: 12px !important;
    border: 1px solid #e5e7eb !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
}

.stTextInput input {
    border-radius: 12px !important;
    border: 1px solid #e5e7eb !important;
    font-family: 'Inter', sans-serif !important;
}

div[data-testid="stFileUploader"] {
    border-radius: 12px !important;
}

.stProgress > div > div {
    background: linear-gradient(90deg, #2563eb, #7c3aed) !important;
    border-radius: 10px !important;
}

/* hide streamlit default elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
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
        return '<span class="score-status status-strong">Strong Match</span>'
    elif score >= 40:
        return '<span class="score-status status-partial">Partial Match</span>'
    else:
        return '<span class="score-status status-low">Needs Work</span>'

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

def animated_progress(label, value, color="blue"):
    st.markdown(f"""
    <div class="progress-wrap">
        <div class="progress-label">
            <span class="progress-name">{label}</span>
            <span class="progress-val">{value}%</span>
        </div>
        <div class="progress-track">
            <div class="progress-fill" style="width: {value}%;"></div>
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
                                  fontSize=20, textColor=colors.HexColor('#2563eb'),
                                  spaceAfter=6)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'],
                                    fontSize=13, textColor=colors.HexColor('#111827'),
                                    spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle('Body', parent=styles['Normal'],
                                 fontSize=10, leading=16,
                                 textColor=colors.HexColor('#374151'))

    story.append(Paragraph("ResumeIQ — Scan Report", title_style))
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
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.HexColor('#eff6ff'), colors.white]),
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

# ── sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">⚡ ResumeIQ</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">Smart resume analysis powered by NLP</div>',
                unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Upload Resume</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name}")

    st.markdown('<div class="sidebar-section">Job Description</div>', unsafe_allow_html=True)
    jd_text = st.text_area("", height=200, placeholder="Paste the full job description here...",
                            label_visibility="collapsed")

    st.markdown('<div class="sidebar-section">PDF Report Password</div>',
                unsafe_allow_html=True)
    pdf_password = st.text_input("", type="password", placeholder="Set a password...",
                                  label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    scan_clicked = st.button("⚡ Scan My Resume", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.72rem; color:#9ca3af; line-height:1.8;">
        <b style="color:#6b7280;">How it works</b><br>
        1. Upload your resume PDF<br>
        2. Paste a job description<br>
        3. Set a PDF password<br>
        4. Click Scan My Resume<br>
        5. Download your report
    </div>
    """, unsafe_allow_html=True)

# ── main area ─────────────────────────────────────────────────
st.markdown("""
<div class="main-hero">
    <div class="hero-title">Smart Resume <span>Keyword Scanner</span></div>
    <div class="hero-sub">
        Match your resume against any job description and get instant AI-powered insights
    </div>
</div>
""", unsafe_allow_html=True)

if not scan_clicked:
    st.markdown("""
    <div class="section-card">
        <div class="empty-state">
            <div class="empty-icon">⚡</div>
            <div class="empty-title">Ready to scan your resume</div>
            <div class="empty-sub">
                Upload your resume, paste a job description,
                and click Scan My Resume in the sidebar to get started
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    if not uploaded_file:
        st.warning("⚠️ Please upload your resume PDF in the sidebar.")
    elif not jd_text.strip():
        st.warning("⚠️ Please paste a job description in the sidebar.")
    elif not pdf_password.strip():
        st.warning("⚠️ Please set a password for your PDF report.")
    else:
        with st.spinner("✨ Analyzing your resume..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            time.sleep(0.5)

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

        # stat cards row
        st.markdown(f"""
        <div class="stats-row">
            <div class="stat-card">
                <div class="stat-number blue">{overall}%</div>
                <div class="stat-label">Overall Match</div>
            </div>
            <div class="stat-card">
                <div class="stat-number purple">{skill_sc}%</div>
                <div class="stat-label">Skills Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-number green">{len(all_matched)}</div>
                <div class="stat-label">Keywords Matched</div>
            </div>
            <div class="stat-card">
                <div class="stat-number orange">{len(missing_skills)}</div>
                <div class="stat-label">Keywords Missing</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])

        with col1:
            # score card
            st.markdown(f"""
            <div class="section-card">
                <div class="card-header">
                    <div class="card-icon blue">🎯</div>
                    <div>
                        <div class="card-title">Overall Match Score</div>
                        <div class="card-subtitle">Based on full keyword analysis</div>
                    </div>
                </div>
                <div class="score-display">
                    <div class="score-big">{overall}%</div>
                    <div>{get_status(overall)}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # progress bars card
            st.markdown("""
            <div class="section-card">
                <div class="card-header">
                    <div class="card-icon purple">📊</div>
                    <div>
                        <div class="card-title">Score Breakdown</div>
                        <div class="card-subtitle">By resume category</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            animated_progress("Skills", skill_sc)
            animated_progress("Experience", exp_sc)
            animated_progress("Education", edu_sc)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            # keywords card
            found_pills = " ".join([f'<span class="pill pill-found">{kw}</span>'
                                    for kw in sorted(all_matched)])
            missing_pills = " ".join([f'<span class="pill pill-missing">{kw}</span>'
                                      for kw in sorted(missing_skills)])
            st.markdown(f"""
            <div class="section-card">
                <div class="card-header">
                    <div class="card-icon green">🔑</div>
                    <div>
                        <div class="card-title">Keyword Analysis</div>
                        <div class="card-subtitle">{len(all_matched)} matched · {len(missing_skills)} missing</div>
                    </div>
                </div>
                <div style="margin-bottom:1rem;">
                    <div style="font-size:0.78rem;font-weight:700;color:#059669;
                                text-transform:uppercase;letter-spacing:0.05em;
                                margin-bottom:8px;">
                        ✅ Matched
                    </div>
                    <div class="pills-wrap">{found_pills if found_pills else '<span style="color:#9ca3af;font-size:0.82rem;">None found</span>'}</div>
                </div>
                <div>
                    <div style="font-size:0.78rem;font-weight:700;color:#dc2626;
                                text-transform:uppercase;letter-spacing:0.05em;
                                margin-bottom:8px;">
                        ❌ Missing
                    </div>
                    <div class="pills-wrap">{missing_pills if missing_pills else '<span style="color:#9ca3af;font-size:0.82rem;">None — great job!</span>'}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # suggestions card
            suggestions_html = ""
            for i, tip in enumerate(suggestions, 1):
                suggestions_html += f"""
                <div class="suggestion-item">
                    <div class="suggestion-num">{i}</div>
                    <div class="suggestion-text">{tip}</div>
                </div>"""
            st.markdown(f"""
            <div class="section-card">
                <div class="card-header">
                    <div class="card-icon orange">💡</div>
                    <div>
                        <div class="card-title">Smart Suggestions</div>
                        <div class="card-subtitle">AI-powered improvement tips</div>
                    </div>
                </div>
                {suggestions_html}
            </div>
            """, unsafe_allow_html=True)

        # export card
        st.markdown("""
        <div class="section-card">
            <div class="card-header">
                <div class="card-icon blue">📥</div>
                <div>
                    <div class="card-title">Export Report</div>
                    <div class="card-subtitle">Download your full analysis as PDF</div>
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
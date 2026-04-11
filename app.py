import streamlit as st
import pdfplumber
import re
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from io import BytesIO

# ── custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #e0f0ff 0%, #f0f4ff 40%, #e8f0fe 100%);
    min-height: 100vh;
}

.main-header {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
}

.main-header h1 {
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #1a73e8, #6c63ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.4rem;
}

.main-header p {
    color: #5f6368;
    font-size: 1.05rem;
    font-weight: 400;
}

.glass-card {
    background: rgba(255, 255, 255, 0.55);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.8);
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
}

.section-title {
    font-size: 1rem;
    font-weight: 600;
    color: #1a73e8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 1rem;
}

.score-circle {
    text-align: center;
    padding: 1.5rem;
}

.score-number {
    font-size: 4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #1a73e8, #6c63ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
}

.score-label {
    font-size: 0.9rem;
    color: #5f6368;
    margin-top: 0.4rem;
    font-weight: 500;
}

.metric-card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.9);
    box-shadow: 0 4px 16px rgba(31, 38, 135, 0.08);
    padding: 1.2rem 1rem;
    text-align: center;
    margin-bottom: 0.5rem;
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #1a73e8;
}

.metric-label {
    font-size: 0.8rem;
    color: #5f6368;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.keyword-tag-found {
    display: inline-block;
    background: rgba(52, 168, 83, 0.12);
    color: #1e7e34;
    border: 1px solid rgba(52, 168, 83, 0.3);
    border-radius: 20px;
    padding: 4px 12px;
    margin: 3px;
    font-size: 0.8rem;
    font-weight: 500;
}

.keyword-tag-missing {
    display: inline-block;
    background: rgba(234, 67, 53, 0.1);
    color: #c0392b;
    border: 1px solid rgba(234, 67, 53, 0.25);
    border-radius: 20px;
    padding: 4px 12px;
    margin: 3px;
    font-size: 0.8rem;
    font-weight: 500;
}

.suggestion-card {
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(10px);
    border-left: 4px solid #1a73e8;
    border-radius: 0 12px 12px 0;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.8rem;
    font-size: 0.92rem;
    color: #2d3748;
    box-shadow: 0 2px 8px rgba(31, 38, 135, 0.06);
}

.badge-strong {
    background: rgba(52, 168, 83, 0.15);
    color: #1e7e34;
    border: 1px solid rgba(52, 168, 83, 0.3);
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 0.8rem;
    font-weight: 600;
}

.badge-partial {
    background: rgba(251, 188, 4, 0.15);
    color: #b45309;
    border: 1px solid rgba(251, 188, 4, 0.3);
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 0.8rem;
    font-weight: 600;
}

.badge-low {
    background: rgba(234, 67, 53, 0.12);
    color: #c0392b;
    border: 1px solid rgba(234, 67, 53, 0.25);
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 0.8rem;
    font-weight: 600;
}

.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(26,115,232,0.2), transparent);
    margin: 1.5rem 0;
}

/* Streamlit widget overrides */
.stTextArea textarea {
    border-radius: 12px !important;
    border: 1px solid rgba(26,115,232,0.25) !important;
    background: rgba(255,255,255,0.7) !important;
    font-family: 'Inter', sans-serif !important;
}

.stTextInput input {
    border-radius: 12px !important;
    border: 1px solid rgba(26,115,232,0.25) !important;
    background: rgba(255,255,255,0.7) !important;
}

.stFileUploader {
    border-radius: 16px !important;
}

.stButton > button {
    background: linear-gradient(135deg, #1a73e8, #6c63ff) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.7rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 4px 15px rgba(26,115,232,0.35) !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    box-shadow: 0 6px 20px rgba(26,115,232,0.5) !important;
    transform: translateY(-1px) !important;
}

.stDownloadButton > button {
    background: linear-gradient(135deg, #34a853, #00b894) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 15px rgba(52,168,83,0.3) !important;
}

.stProgress > div > div {
    background: linear-gradient(90deg, #1a73e8, #6c63ff) !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ── keyword categories ────────────────────────────────────────
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
        "tip": "Add strong action verbs like 'Developed', 'Led', 'Optimized', 'Delivered' at the start of your bullet points."
    },
    "quantified results": {
        "check": ["%", "increased", "reduced", "improved", "saved", "grew"],
        "tip": "Add numbers and metrics to your experience. Example: 'Improved performance by 30%' or 'Managed a team of 5 engineers'."
    },
    "technical skills section": {
        "check": ["skills", "technologies", "tools", "proficient", "expertise"],
        "tip": "Make sure you have a dedicated 'Skills' or 'Technical Skills' section clearly listing your tools and technologies."
    },
    "education details": {
        "check": ["gpa", "cgpa", "grade", "graduated", "degree"],
        "tip": "Include your GPA, graduation year, and full degree name in your Education section."
    },
    "certifications": {
        "check": ["certified", "certification", "certificate", "aws certified",
                  "google certified", "microsoft certified"],
        "tip": "Add any relevant certifications. AWS, Google Cloud or Azure certifications greatly boost your profile."
    },
    "contact information": {
        "check": ["linkedin", "github", "portfolio", "email", "phone"],
        "tip": "Make sure your resume includes LinkedIn, GitHub, email and phone number at the top."
    },
    "summary section": {
        "check": ["summary", "objective", "profile", "about"],
        "tip": "Add a 2-3 line professional summary at the top highlighting your experience and goals."
    },
    "project details": {
        "check": ["project", "projects", "built", "developed", "created"],
        "tip": "Include a Projects section with 2-3 strong projects, tech stack used, and what problem they solve."
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

def get_badge(score):
    if score >= 70:
        return '<span class="badge-strong">Strong</span>'
    elif score >= 40:
        return '<span class="badge-partial">Partial</span>'
    else:
        return '<span class="badge-low">Low</span>'

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
            f"{', '.join(top_missing)} — these appear in the job description but not in your resume."
        )
    if not suggestions:
        suggestions.append("Great job! Your resume covers most important areas. "
                           "Consider tailoring your summary specifically for this role.")
    return suggestions[:6]

def generate_pdf(resume_name, overall_score, skill_score, exp_score,
                 edu_score, matched_skills, missing_skills, suggestions, password):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=inch*0.75, leftMargin=inch*0.75,
                            topMargin=inch*0.75, bottomMargin=inch*0.75)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                  fontSize=20, textColor=colors.HexColor('#1a73e8'),
                                  spaceAfter=6)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'],
                                    fontSize=13, textColor=colors.HexColor('#16213e'),
                                    spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle('Body', parent=styles['Normal'],
                                 fontSize=10, leading=16,
                                 textColor=colors.HexColor('#333333'))

    story.append(Paragraph("Resume Keyword Scanner — Report", title_style))
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
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.HexColor('#f0f4ff'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
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
        clean_tip = tip.replace("**", "")
        story.append(Paragraph(f"{i}. {clean_tip}", body_style))
        story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ── UI ────────────────────────────────────────────────────────
st.set_page_config(page_title="Resume Keyword Scanner", page_icon="📄",
                   layout="centered")

# header
st.markdown("""
<div class="main-header">
    <h1>📄 Resume Keyword Scanner</h1>
    <p>Upload your resume · Match with any job · Get instant AI-powered insights</p>
</div>
""", unsafe_allow_html=True)

# input card
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<p class="section-title">📁 Upload & Analyze</p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])
jd_text = st.text_area("Paste the Job Description here", height=180,
                        placeholder="Copy and paste the full job description...")
pdf_password = st.text_input("Set a password for your PDF report",
                              type="password",
                              placeholder="Choose a strong password...")
st.markdown('</div>', unsafe_allow_html=True)

scan_clicked = st.button("🔍 Scan My Resume", use_container_width=True)

if scan_clicked:
    if not uploaded_file:
        st.warning("⚠️ Please upload your resume PDF.")
    elif not jd_text.strip():
        st.warning("⚠️ Please paste a job description.")
    elif not pdf_password.strip():
        st.warning("⚠️ Please set a password for your PDF report.")
    else:
        with st.spinner("✨ Analyzing your resume..."):
            resume_text = extract_text_from_pdf(uploaded_file)

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

        # overall score
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">🎯 Overall Match Score</p>',
                    unsafe_allow_html=True)
        st.markdown(f"""
        <div class="score-circle">
            <div class="score-number">{overall}%</div>
            <div class="score-label">
                {get_badge(overall)}
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(overall / 100)
        st.markdown('</div>', unsafe_allow_html=True)

        # category breakdown
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">📊 Score Breakdown by Category</p>',
                    unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{skill_sc}%</div>
                <div class="metric-label">Skills</div>
            </div>""", unsafe_allow_html=True)
            st.progress(skill_sc / 100)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{exp_sc}%</div>
                <div class="metric-label">Experience</div>
            </div>""", unsafe_allow_html=True)
            st.progress(exp_sc / 100)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{edu_sc}%</div>
                <div class="metric-label">Education</div>
            </div>""", unsafe_allow_html=True)
            st.progress(edu_sc / 100)
        st.markdown('</div>', unsafe_allow_html=True)

        # keywords
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">🔑 Keyword Analysis</p>',
                    unsafe_allow_html=True)
        col4, col5 = st.columns(2)
        with col4:
            st.markdown("**✅ Matched Keywords**")
            tags = " ".join([f'<span class="keyword-tag-found">{kw}</span>'
                             for kw in sorted(all_matched)])
            st.markdown(tags, unsafe_allow_html=True)
        with col5:
            st.markdown("**❌ Missing Keywords**")
            tags = " ".join([f'<span class="keyword-tag-missing">{kw}</span>'
                             for kw in sorted(missing_skills)])
            st.markdown(tags if tags else "None — great job!", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # suggestions
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">💡 Smart Improvement Suggestions</p>',
                    unsafe_allow_html=True)
        for i, tip in enumerate(suggestions, 1):
            st.markdown(f'<div class="suggestion-card">💬 <b>{i}.</b> {tip}</div>',
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # PDF export
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">📥 Export Your Report</p>',
                    unsafe_allow_html=True)
        pdf_buffer = generate_pdf(
            uploaded_file.name, overall, skill_sc, exp_sc, edu_sc,
            all_matched, missing_skills, suggestions, pdf_password
        )
        st.download_button(
            label="⬇️ Download PDF Report",
            data=pdf_buffer,
            file_name="resume_scan_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        st.info(f"🔐 Your PDF password: **{pdf_password}**")
        st.markdown('</div>', unsafe_allow_html=True)
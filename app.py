import streamlit as st
import json
from google import genai
import re

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Antigravity | AI Math Tutor",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS  —  Premium Dark UI
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Dark Background ── */
.stApp {
    background: linear-gradient(135deg, #0d0d1a 0%, #0a0f1e 50%, #0d0d1a 100%);
    color: #e2e8f0;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
    border-right: 1px solid rgba(99,102,241,0.2);
}
section[data-testid="stSidebar"] * {
    color: #cbd5e1 !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stTextInput label {
    color: #94a3b8 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Sidebar selectboxes and inputs ── */
section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stTextInput > div > div > input {
    background: rgba(30,41,59,0.8) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}

/* ── Main content inputs ── */
.stTextInput > div > div > input {
    background: rgba(15,23,42,0.8) !important;
    border: 1px solid rgba(99,102,241,0.4) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    padding: 12px 16px !important;
    font-size: 0.95rem !important;
    transition: border-color 0.2s ease;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(99,102,241,0.9) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}
.stTextInput > div > div > input::placeholder {
    color: #475569 !important;
}
.stTextInput label {
    color: #94a3b8 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 4px !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.03em;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(99,102,241,0.45) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
}

/* ── Progress Bar ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #a78bfa) !important;
    border-radius: 100px !important;
}
.stProgress > div > div {
    background: rgba(30,41,59,0.7) !important;
    border-radius: 100px !important;
    height: 10px !important;
}

/* ── Divider ── */
hr {
    border-color: rgba(99,102,241,0.15) !important;
}

/* ── Alert / Info Boxes ── */
.stAlert {
    border-radius: 12px !important;
    border: none !important;
}
div[data-testid="stNotification"] {
    background: rgba(15,23,42,0.9) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
}

/* ── Expander ── */
details {
    background: rgba(15,23,42,0.5) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 12px !important;
}
summary {
    color: #a5b4fc !important;
    font-weight: 600;
    padding: 12px 16px !important;
}

/* ── Custom Card Styles (injected via HTML) ── */
.ag-hero {
    background: linear-gradient(135deg, rgba(99,102,241,0.08) 0%, rgba(139,92,246,0.05) 100%);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 20px;
    padding: 32px 36px;
    margin-bottom: 28px;
}
.ag-hero h1 {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a5b4fc, #c4b5fd, #e879f9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 8px 0;
    line-height: 1.2;
}
.ag-hero p {
    color: #64748b;
    font-size: 1.05rem;
    margin: 0;
}

.ag-phase-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 28px 0 16px 0;
}
.ag-phase-number {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    font-weight: 700;
    flex-shrink: 0;
}
.ag-phase-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #e2e8f0;
    margin: 0;
}
.ag-phase-subtitle {
    font-size: 0.82rem;
    color: #475569;
    margin: 2px 0 0 44px;
}

.ag-card {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 16px;
    padding: 24px;
    margin: 10px 0;
    backdrop-filter: blur(10px);
}
.ag-card-success {
    background: rgba(16,185,129,0.08);
    border-color: rgba(16,185,129,0.3);
}
.ag-card-error {
    background: rgba(239,68,68,0.08);
    border-color: rgba(239,68,68,0.3);
}
.ag-card-info {
    background: rgba(99,102,241,0.07);
    border-color: rgba(99,102,241,0.25);
}
.ag-card-warn {
    background: rgba(245,158,11,0.08);
    border-color: rgba(245,158,11,0.3);
}

.ag-question-box {
    background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(139,92,246,0.08));
    border: 1px solid rgba(99,102,241,0.35);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 14px;
}
.ag-question-box .q-icon { font-size: 1.5rem; }
.ag-question-box .q-text {
    font-size: 1.1rem;
    font-weight: 600;
    color: #c4b5fd;
    font-family: 'Courier New', monospace;
}
.ag-question-box .q-label {
    font-size: 0.72rem;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.ag-stat {
    background: rgba(15,23,42,0.7);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}
.ag-stat .stat-value {
    font-size: 1.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a5b4fc, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.ag-stat .stat-label {
    font-size: 0.75rem;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4px;
}

.ag-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, rgba(245,158,11,0.15), rgba(234,179,8,0.1));
    border: 1px solid rgba(245,158,11,0.4);
    border-radius: 100px;
    padding: 6px 16px;
    font-size: 0.85rem;
    font-weight: 600;
    color: #fbbf24;
    margin: 4px;
}

.ag-level-easy { color: #34d399; }
.ag-level-medium { color: #fbbf24; }
.ag-level-hard { color: #f87171; }

.ag-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.3), transparent);
    margin: 32px 0;
}

.ag-sidebar-logo {
    font-size: 1.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a5b4fc, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}
.ag-sidebar-tagline {
    font-size: 0.75rem;
    color: #475569;
    margin-bottom: 20px;
}

.ag-step-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: #6366f1;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; max-width: 1100px !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    "llm_calls": 0,
    "generated_question": None,
    "difficulty": "easy",
    "correct_streak": 0,
    "teaching_content": None,
    "reteach_content": None,
    "mastered": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

MAX_CALLS = 10

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
with open("dataset.json", encoding="utf-8") as f:
    dataset = json.load(f)
with open("students.json", encoding="utf-8") as f:
    students = json.load(f)
with open("system_prompt.txt", encoding="utf-8") as f:
    system_prompt = f.read()

QC_TO_SKILL = {
    "Linear Equation – Basic": "Linear Equations",
    "Linear Equation – Variables on Both Sides": "Linear Equations",
    "Integer Operations": "Number System",
    "Factorization – Difference of Squares": "Factorization",
    "Sequence Pattern": "Sequences"
}

DEMO_QUESTIONS = {
    "Linear Equation – Basic": "2x + 3 = 7",
    "Linear Equation – Variables on Both Sides": "2x + 3 = 7",
    "Integer Operations": "-5 + 3",
    "Factorization – Difference of Squares": "x^2 - 9",
    "Sequence Pattern": "2, 4, 8, 16",
}

# ─────────────────────────────────────────────
# AI FUNCTIONS
# ─────────────────────────────────────────────
def get_teaching_content(topic, grade, api_key):
    try:
        client = genai.Client(api_key=api_key)
        with open("teaching_prompt.txt", encoding="utf-8") as f:
            tmpl = f.read()
        prompt = tmpl.replace("{topic}", topic).replace("{grade}", grade)
        return client.models.generate_content(model="gemini-2.0-flash", contents=prompt).text
    except Exception as e:
        return f"Error: {e}"

def get_reteach_content(topic, confusion, api_key):
    try:
        client = genai.Client(api_key=api_key)
        with open("reteach_prompt.txt", encoding="utf-8") as f:
            tmpl = f.read()
        prompt = tmpl.replace("{topic}", topic).replace("{confusion}", confusion)
        return client.models.generate_content(model="gemini-2.0-flash", contents=prompt).text
    except Exception as e:
        return f"Error: {e}"

def get_llm_feedback(question, student_answer, correct_answer, system_prompt, api_key):
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""{system_prompt}

Question: {question}
Student Answer: {student_answer}
Correct Answer: {correct_answer}

Return JSON only:
{{
  "error_type": "...",
  "reason": "...",
  "step_error": "...",
  "hint": "..."
}}"""
        return client.models.generate_content(model="gemini-2.0-flash", contents=prompt).text
    except Exception as e:
        return f'{{"error_type": "API Error", "reason": "{str(e)}", "step_error": "N/A", "hint": "N/A"}}'

def generate_similar_question(question, qc, difficulty, api_key):
    try:
        client = genai.Client(api_key=api_key)
        with open("generation_prompt.txt", encoding="utf-8") as f:
            gen_prompt = f.read()
        prompt = f"{gen_prompt}\n\nOriginal Question: {question}\nQC: {qc}\nDifficulty Level: {difficulty}"
        return client.models.generate_content(model="gemini-2.0-flash", contents=prompt).text.strip().split("\n")[0]
    except Exception as e:
        return f"Error: {e}"

def demo_ai_response():
    return {
        "error_type": "Sign Error",
        "reason": "The constant was moved across '=' without flipping its sign.",
        "step_error": "Step 2: Isolate variable",
        "hint": "When moving a term across '=', always flip its sign."
    }

def analyze_student(student):
    skill_errors = {}
    for attempt in student["attempts"]:
        q = attempt["question"].replace(" ", "").lower()
        s_ans = attempt["student_answer"].replace(" ", "").lower()
        match = next((d for d in dataset if d["question"].replace(" ", "").lower() == q), None)
        if not match: continue
        if s_ans != match["answer"].replace(" ", "").lower():
            skill = QC_TO_SKILL.get(match["qc"], "Unknown")
            skill_errors[skill] = skill_errors.get(skill, 0) + 1
    return skill_errors

def diagnose(skill_errors):
    return {skill: ("🔴 Weak" if c >= 2 else "🟡 Needs Practice") for skill, c in skill_errors.items()}


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="ag-sidebar-logo">⚡ Antigravity</div>', unsafe_allow_html=True)
    st.markdown('<div class="ag-sidebar-tagline">AI-Powered Math Tutor System</div>', unsafe_allow_html=True)
    st.divider()

    st.markdown("**⚙️ Configuration**")
    grade = st.selectbox("Grade Level", ["6", "7", "8"], label_visibility="collapsed")
    st.caption(f"Grade {grade} Curriculum")
    topic = st.selectbox("Math Topic", list(QC_TO_SKILL.keys()), label_visibility="collapsed")

    st.divider()

    st.markdown("**🔑 AI Engine**")
    api_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...", label_visibility="collapsed")
    if api_key:
        st.success("✓ API Connected", icon="🟢")
    else:
        st.caption("No key? [Get one free →](https://aistudio.google.com/app/apikey)")

    st.divider()

    # Level indicator in sidebar
    levels = ["easy", "medium", "hard"]
    lvl_colors = {"easy": "#34d399", "medium": "#fbbf24", "hard": "#f87171"}
    lvl_icons  = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}
    cur = st.session_state.difficulty
    st.markdown(f"**📊 Session Stats**")
    st.markdown(f"""
    <div style="display:flex;gap:8px;margin-top:8px;">
        <div style="flex:1;background:rgba(15,23,42,0.8);border:1px solid rgba(99,102,241,0.2);border-radius:10px;padding:10px;text-align:center;">
            <div style="font-size:1.4rem;font-weight:800;color:{lvl_colors[cur]};">{st.session_state.correct_streak}</div>
            <div style="font-size:0.65rem;color:#475569;text-transform:uppercase;letter-spacing:0.08em;">Streak</div>
        </div>
        <div style="flex:1;background:rgba(15,23,42,0.8);border:1px solid rgba(99,102,241,0.2);border-radius:10px;padding:10px;text-align:center;">
            <div style="font-size:1rem;font-weight:700;color:{lvl_colors[cur]};">{lvl_icons[cur]} {cur.upper()}</div>
            <div style="font-size:0.65rem;color:#475569;text-transform:uppercase;letter-spacing:0.08em;">Level</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    prog_val = (levels.index(cur) + 1) / 3
    st.caption(f"Mastery Progress — {int(prog_val * 100)}%")
    st.progress(prog_val)

    if st.session_state.mastered:
        st.markdown(f'<div class="ag-badge">🏆 {topic} Master</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="ag-hero">
    <h1>Antigravity AI Tutor</h1>
    <p>Not a solver. Not a checker. A system that teaches you how to <strong style="color:#a5b4fc;">think</strong>.</p>
</div>
""", unsafe_allow_html=True)

# Active question
q = DEMO_QUESTIONS.get(topic, "2x + 3 = 7")
match = next((d for d in dataset if d["question"].replace(" ", "").lower() == q.replace(" ", "").lower()), None)
correct = match["answer"] if match else "N/A"


# ─────────────────────────────────────────────
# PHASE 1 — TEACH
# ─────────────────────────────────────────────
st.markdown("""
<div class="ag-phase-header">
    <div class="ag-phase-number">1</div>
    <div>
        <p class="ag-phase-title">🧠 Learn the Concept</p>
    </div>
</div>
<p class="ag-phase-subtitle">Let the AI tutor explain this topic before you attempt any problem.</p>
""", unsafe_allow_html=True)

col_teach_btn, col_teach_info = st.columns([1, 3])
with col_teach_btn:
    teach_clicked = st.button("🎓 Teach Me", use_container_width=True)

with col_teach_info:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;padding:10px 0;">
        <div style="background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.25);border-radius:8px;padding:8px 14px;">
            <span style="color:#a5b4fc;font-weight:600;font-size:0.85rem;">📘 {topic}</span>
        </div>
        <div style="background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.25);border-radius:8px;padding:8px 14px;">
            <span style="color:#a5b4fc;font-weight:600;font-size:0.85rem;">🎓 Grade {grade}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

if teach_clicked:
    if api_key and st.session_state.llm_calls < MAX_CALLS:
        with st.spinner("Preparing your personalised lesson..."):
            st.session_state.teaching_content = get_teaching_content(topic, grade, api_key)
            st.session_state.llm_calls += 1
    else:
        st.session_state.teaching_content = f"""**Demo Lesson: {topic}** (Grade {grade})

Think of an equation like a **perfectly balanced scale** ⚖️

Whatever you do to one side, you MUST do to the other — otherwise the scale tips and everything breaks.

**Key Idea: Isolate the variable by doing the same operation on BOTH sides.**

**Example:** Solve 2x + 4 = 10
1. Subtract 4 from both sides → 2x = 6
2. Divide both sides by 2     → x = 3  ✅

*Add your Gemini API key in the sidebar for a fully personalised lesson!*"""

if st.session_state.teaching_content:
    st.markdown(f"""
    <div class="ag-card ag-card-info">
        <div style="font-size:0.75rem;color:#6366f1;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">📖 AI Lesson</div>
        <div style="color:#cbd5e1;line-height:1.75;white-space:pre-line;">{st.session_state.teaching_content}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="ag-divider"></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PHASE 2 — STEP-BY-STEP SOLVE
# ─────────────────────────────────────────────
st.markdown("""
<div class="ag-phase-header">
    <div class="ag-phase-number">2</div>
    <div>
        <p class="ag-phase-title">✍️ Solve Step by Step</p>
    </div>
</div>
<p class="ag-phase-subtitle">Show your thinking. Don't just give a final answer.</p>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="ag-question-box">
    <div class="q-icon">❓</div>
    <div>
        <div class="q-label">Your Problem</div>
        <div class="q-text">{q}</div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="ag-step-label">① First Move</div>', unsafe_allow_html=True)
    step1 = st.text_input("Step 1", placeholder="e.g. subtract 3 from both sides", label_visibility="collapsed")
with col2:
    st.markdown('<div class="ag-step-label">② New Equation</div>', unsafe_allow_html=True)
    step2 = st.text_input("Step 2", placeholder="e.g. 2x = 4", label_visibility="collapsed")
with col3:
    st.markdown('<div class="ag-step-label">③ Final Answer</div>', unsafe_allow_html=True)
    final_ans = st.text_input("Final Answer", placeholder="e.g. x = 2", label_visibility="collapsed")

submit_answer = st.button("⚡ Evaluate My Thinking", use_container_width=False)

# ─────────────────────────────────────────────
# EVALUATION LOGIC + PHASES 3–5
# ─────────────────────────────────────────────
if submit_answer and final_ans:
    if not match:
        st.warning("⚠️ Question not found in dataset. Please select a topic from the sidebar.")
    else:
        is_correct = str(final_ans).replace(" ", "").lower() == str(correct).replace(" ", "").lower()

        st.markdown('<div class="ag-divider"></div>', unsafe_allow_html=True)

        if is_correct:
            # ── CORRECT ──
            st.session_state.correct_streak += 1

            if st.session_state.correct_streak >= 2:
                if st.session_state.difficulty == "easy":
                    st.session_state.difficulty = "medium"
                    st.toast("🟡 Level Up! Now on MEDIUM", icon="🚀")
                elif st.session_state.difficulty == "medium":
                    st.session_state.difficulty = "hard"
                    st.toast("🔴 Level Up! Now on HARD", icon="🏆")

            if st.session_state.correct_streak >= 3:
                st.session_state.mastered = True

            st.markdown(f"""
            <div class="ag-card ag-card-success">
                <div style="font-size:1.5rem;font-weight:800;color:#34d399;margin-bottom:6px;">
                    ✅ Correct!
                </div>
                <div style="color:#6ee7b7;font-size:0.95rem;">
                    The answer is <strong>{correct}</strong>. 
                    {"You're on 🔥 Streak " + str(st.session_state.correct_streak) + "!" if st.session_state.correct_streak > 1 else "Great work! Keep going."}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.mastered:
                st.balloons()
                st.markdown(f"""
                <div style="text-align:center;padding:20px 0;">
                    <div style="font-size:2rem;margin-bottom:8px;">🏆</div>
                    <div style="font-size:1.3rem;font-weight:800;background:linear-gradient(135deg,#fbbf24,#f59e0b);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                        Concept Mastered!
                    </div>
                    <div style="color:#94a3b8;font-size:0.9rem;margin-top:6px;">You've earned the <strong style="color:#fbbf24;">{topic} Master</strong> badge</div>
                </div>
                """, unsafe_allow_html=True)

        else:
            # ── INCORRECT ──
            st.session_state.correct_streak = 0
            st.session_state.difficulty = "easy"
            st.session_state.mastered = False

            error_type = match.get("common_error", "Unknown Error")
            is_conceptual = "Concept" in error_type or "Pattern" in error_type

            # Phase 3 header
            st.markdown("""
            <div class="ag-phase-header">
                <div class="ag-phase-number">3</div>
                <div><p class="ag-phase-title">🔍 Diagnosis</p></div>
            </div>
            """, unsafe_allow_html=True)

            col_rule, col_ai = st.columns(2)

            with col_rule:
                st.markdown(f"""
                <div class="ag-card ag-card-error">
                    <div style="font-size:0.72rem;color:#fc8181;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">📌 Rule Engine</div>
                    <div style="color:#fca5a5;font-weight:700;font-size:1rem;margin-bottom:8px;">
                        {'⚠️ Conceptual Error' if is_conceptual else '❌ Operational Mistake'}
                    </div>
                    <div style="color:#9ca3af;font-size:0.88rem;line-height:1.6;">
                        <strong style="color:#f87171;">Error Type:</strong> {error_type}<br>
                        <strong style="color:#f87171;">Expected:</strong> <code style="background:rgba(239,68,68,0.1);padding:2px 6px;border-radius:4px;color:#fca5a5;">{correct}</code>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_ai:
                parsed = None
                if api_key and st.session_state.llm_calls < MAX_CALLS:
                    with st.spinner("🤖 Analysing your thinking..."):
                        raw = get_llm_feedback(q, final_ans, correct, system_prompt, api_key)
                        st.session_state.llm_calls += 1
                    try:
                        parsed = json.loads(re.sub(r'```json\n|\n```', '', raw).strip())
                    except:
                        pass
                else:
                    parsed = demo_ai_response()

                if parsed:
                    st.markdown(f"""
                    <div class="ag-card ag-card-warn">
                        <div style="font-size:0.72rem;color:#fbbf24;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">🤖 AI Tutor Analysis</div>
                        <div style="color:#9ca3af;font-size:0.88rem;line-height:1.8;">
                            <strong style="color:#fbbf24;">Why:</strong> {parsed.get('reason', 'N/A')}<br>
                            <strong style="color:#fbbf24;">Step Error:</strong> {parsed.get('step_error', 'N/A')}<br>
                            <strong style="color:#fbbf24;">Hint:</strong> 💡 {parsed.get('hint', 'N/A')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # ── PHASE 4: RETEACH ──
            st.markdown('<div class="ag-divider"></div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="ag-phase-header">
                <div class="ag-phase-number">4</div>
                <div><p class="ag-phase-title">🔄 Still Confused? Let's Try a Different Angle.</p></div>
            </div>
            """, unsafe_allow_html=True)

            confusion = st.text_input("💬 What didn't make sense?", placeholder="e.g. I don't understand why the sign changes when moving to the other side")
            reteach_btn = st.button("🔁 Explain Differently", use_container_width=False)

            if reteach_btn and confusion:
                if api_key and st.session_state.llm_calls < MAX_CALLS:
                    with st.spinner("Rethinking the approach..."):
                        st.session_state.reteach_content = get_reteach_content(topic, confusion, api_key)
                        st.session_state.llm_calls += 1
                else:
                    st.session_state.reteach_content = "Think of it this way: the equals sign is like a bridge with a toll ⚖️. When a number *crosses the bridge*, it has to pay — meaning its sign flips. Positive becomes negative and vice versa. No exceptions!"

            if st.session_state.reteach_content:
                st.markdown(f"""
                <div class="ag-card ag-card-info" style="margin-top:12px;">
                    <div style="font-size:0.72rem;color:#818cf8;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">🔁 Alternative Explanation</div>
                    <div style="color:#cbd5e1;line-height:1.75;white-space:pre-line;">{st.session_state.reteach_content}</div>
                </div>
                """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PHASE 5 — PRACTICE & PROGRESS
# ─────────────────────────────────────────────
st.markdown('<div class="ag-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="ag-phase-header">
    <div class="ag-phase-number">5</div>
    <div><p class="ag-phase-title">📈 Practice & Progress</p></div>
</div>
<p class="ag-phase-subtitle">Never stop at one question. Build mastery through repetition.</p>
""", unsafe_allow_html=True)

# Progress stats row
c1, c2, c3 = st.columns(3)
lvl = st.session_state.difficulty
with c1:
    st.markdown(f"""
    <div class="ag-stat">
        <div class="stat-value ag-level-{lvl}">{lvl.upper()}</div>
        <div class="stat-label">Current Level</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="ag-stat">
        <div class="stat-value">{st.session_state.correct_streak}</div>
        <div class="stat-label">Correct Streak</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    progress_pct = int(((levels.index(lvl) + 1) / 3) * 100)
    st.markdown(f"""
    <div class="ag-stat">
        <div class="stat-value">{progress_pct}%</div>
        <div class="stat-label">Mastery Score</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.progress((levels.index(lvl) + 1) / 3)

gen_btn = st.button("🎲 Generate Practice Question", use_container_width=False)
if gen_btn:
    if api_key and st.session_state.llm_calls < MAX_CALLS:
        with st.spinner(f"Crafting a {lvl.upper()} level question for you..."):
            new_q = generate_similar_question(q, topic, lvl, api_key)
            st.session_state.llm_calls += 1
            st.session_state.generated_question = new_q
    else:
        st.session_state.generated_question = "3x − 5 = 10"

if st.session_state.generated_question:
    st.markdown(f"""
    <div class="ag-question-box" style="margin-top:16px;">
        <div class="q-icon">🆕</div>
        <div>
            <div class="q-label">New {lvl.upper()} Practice Question</div>
            <div class="q-text">{st.session_state.generated_question}</div>
        </div>
    </div>
    <div style="color:#475569;font-size:0.8rem;margin-top:-4px;margin-left:2px;">
        ↑ Type this question into Step 2 above to evaluate your answer.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# TEACHER VIEW (COLLAPSIBLE)
# ─────────────────────────────────────────────
st.markdown('<div class="ag-divider"></div>', unsafe_allow_html=True)
with st.expander("📊 Teacher View — Batch Analytics"):
    student_ids = [s["student_id"] for s in students]
    selected_id = st.selectbox("Select Student Profile", student_ids)
    student = next(s for s in students if s["student_id"] == selected_id)
    errors = analyze_student(student)
    diag = diagnose(errors)

    if not errors:
        st.success("✅ No errors detected. Student is performing well across all skills.")
    else:
        st.markdown("**Error Breakdown by Skill:**")
        for skill, count in errors.items():
            c, d = st.columns([3, 1])
            with c:
                pct = min(count / 5, 1.0)
                st.progress(pct, text=f"**{skill}** — {count} error(s)")
            with d:
                st.write(diag[skill])

import streamlit as st
import json
from google import genai
import re

# -------- SETUP & SESSION STATE --------
st.set_page_config(page_title="Learning Intelligence Engine", layout="wide")

if "llm_calls" not in st.session_state:
    st.session_state.llm_calls = 0

if "generated_question" not in st.session_state:
    st.session_state.generated_question = None

if "difficulty" not in st.session_state:
    st.session_state.difficulty = "easy"

if "correct_streak" not in st.session_state:
    st.session_state.correct_streak = 0

MAX_CALLS = 3

# -------- LOAD DATA --------
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

# -------- AI FUNCTIONS --------
def get_llm_feedback(question, student_answer, correct_answer, system_prompt, api_key):
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
{system_prompt}

Question: {question}
Student Answer: {student_answer}
Correct Answer: {correct_answer}

Return JSON only:
{{
  "error_type": "...",
  "reason": "...",
  "step_error": "...",
  "hint": "..."
}}
"""
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f'{{"error_type": "API Error", "reason": "{str(e)}", "step_error": "N/A", "hint": "N/A"}}'

def generate_similar_question(question, qc, difficulty, api_key):
    try:
        client = genai.Client(api_key=api_key)
        
        with open("generation_prompt.txt", encoding="utf-8") as f:
            gen_prompt = f.read()

        prompt = f"""
{gen_prompt}

Original Question: {question}
QC: {qc}
Difficulty Level: {difficulty}
"""
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        # Clean output: strip whitespace and take ONLY the first line to be safe
        clean_q = response.text.strip().split("\n")[0]
        return clean_q
    except Exception as e:
        return f"Error generating question: {str(e)}"

def demo_ai_response(question, student_answer):
    return {
        "error_type": "Sign Error",
        "reason": "You moved the constant incorrectly across the equation. The sign should change when shifting sides.",
        "step_error": "Step 2: Isolate variable",
        "hint": "When moving a term across '=', always flip its sign."
    }

def analyze_student(student):
    skill_errors = {}
    for attempt in student["attempts"]:
        q = attempt["question"].replace(" ", "").lower()
        student_ans = attempt["student_answer"].replace(" ", "").lower()
        match = next((d for d in dataset if d["question"].replace(" ", "").lower() == q), None)
        if not match: continue
        if student_ans != match["answer"].replace(" ", "").lower():
            skill = QC_TO_SKILL.get(match["qc"], "Unknown")
            skill_errors[skill] = skill_errors.get(skill, 0) + 1
    return skill_errors

def diagnose(skill_errors):
    diagnosis = {}
    for skill, count in skill_errors.items():
        if count >= 2: diagnosis[skill] = "🔴 Weak"
        else: diagnosis[skill] = "🟡 Needs Practice"
    return diagnosis

# -------- UI: HEADER --------
st.markdown("""
# 🚀 Learning Intelligence Engine

### 🧠 What this does:
- Identifies *why* a student is wrong
- Maps mistakes to underlying skills
- Generates step-level feedback using AI

👉 This is not a solver. It’s a **diagnostic learning system**.
---
""")

# -------- SIDEBAR --------
st.sidebar.header("🔑 LLM Settings")
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

with st.sidebar.expander("🔑 How to get your Gemini API key"):
    st.markdown("""
1. Go to: [Google AI Studio](https://aistudio.google.com/app/apikey)  
2. Click **Create API Key**  
3. Copy and paste it above  

⚡ No billing needed for basic usage.
""")

st.sidebar.markdown("---")

st.sidebar.header("🎯 Demo Mode")
demo_question = st.sidebar.selectbox(
    "Try Example",
    [
        "2x + 3 = 7",
        "x^2 - 9",
        "-5 + 3",
        "2, 4, 8, 16"
    ]
)

# -------- DEMO SECTION --------
st.header("🎯 Interactive Diagnosis Demo")

q = st.text_input("Enter Question", value=demo_question)
student_ans = st.text_input(
    "Student Answer",
    value="x = -2" if q == "2x + 3 = 7" else ""
)

if q and student_ans:
    match = next((d for d in dataset if d["question"].replace(" ", "").lower() == q.replace(" ", "").lower()), None)

    if not match:
        st.warning("Question not in dataset. Try a guided example.")
    else:
        correct = match["answer"]
        if str(student_ans).replace(" ", "").lower() == str(correct).replace(" ", "").lower():
            st.success(f"✅ Correct! The answer is {correct}. You're on fire! 🔥")
            st.session_state.correct_streak += 1
            
            # Level Up Logic
            if st.session_state.correct_streak >= 2:
                if st.session_state.difficulty == "easy":
                    st.session_state.difficulty = "medium"
                    st.toast("Level Up: Medium! 🟡", icon="🚀")
                elif st.session_state.difficulty == "medium":
                    st.session_state.difficulty = "hard"
                    st.toast("Level Up: Hard! 🔴", icon="🏆")
                st.session_state.correct_streak = 0
        else:
            st.session_state.correct_streak = 0
            st.session_state.difficulty = "easy" # Reset to Easy to master fundamentals
            
            # Severity
            error_type = match['common_error']
            if "Concept" in error_type or "Pattern" in error_type:
                st.error("🔴 Conceptual misunderstanding detected")
            else:
                st.warning("🟡 Operational mistake detected")

        # --- 📈 LEARNING PROGRESS ---
        st.markdown("### 📈 Learning Progress")
        levels = ["easy", "medium", "hard"]
        progress_val = (levels.index(st.session_state.difficulty) + 1) / 3
        
        st.progress(progress_val)
        status_cols = st.columns(3)
        with status_cols[0]:
            st.write(f"Level: **{st.session_state.difficulty.upper()}**")
        with status_cols[1]:
            st.write(f"Streak: **{st.session_state.correct_streak}** / 2")
        with status_cols[2]:
            st.info(f"Target: {st.session_state.difficulty.upper()} Mastery")

        # Result Card
        st.markdown("## 🧠 Diagnosis")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📌 Rule Engine")
            st.write(f"**Target QC:** {match['qc']}")
            st.info(f"**Error Type:** {error_type}")
            st.write(f"**Expected Answer:** `{correct}`")

        with col2:
            st.markdown("### 🤖 AI Diagnosis")
            
            parsed = None
            llm_output = ""

            if api_key and st.session_state.llm_calls < MAX_CALLS:
                with st.spinner("Generating deep reasoning..."):
                    llm_output = get_llm_feedback(q, student_ans, correct, system_prompt, api_key)
                    st.session_state.llm_calls += 1
                
                try:
                    clean_output = re.sub(r'```json\n|\n```', '', llm_output).strip()
                    parsed = json.loads(clean_output)
                except Exception:
                    pass
            else:
                if not api_key:
                    st.info("🤖 AI is currently in *demo mode* (saving my wallet 💸).\n\nWant real intelligence?\n👉 Add your Gemini API key in the sidebar.\n\nDon’t worry — it takes 30 seconds.")
                elif st.session_state.llm_calls >= MAX_CALLS:
                    st.warning("⚠️ Live AI limit reached. Switching to demo mode.")
                
                parsed = demo_ai_response(q, student_ans)

            if parsed:
                st.success(f"**Error:** {parsed.get('error_type', 'Unknown')}")
                st.write(f"**Why:** {parsed.get('reason', 'N/A')}")
                st.write(f"**Step Error:** {parsed.get('step_error', 'N/A')}")
                st.info(f"💡 **Hint:** {parsed.get('hint', 'N/A')}")
            else:
                st.code(llm_output)

        # --- 🎯 TARGETED INTERVENTION ---
        st.markdown("---")
        st.markdown("### 🎯 Targeted Intervention")
        
        focus_skill = QC_TO_SKILL.get(match["qc"], "this concept")
        hint_text = parsed.get("hint", "Focus on correct step execution") if parsed else "Check your calculations carefully."
        step_error = parsed.get("step_error", "Check your steps carefully") if parsed else "n/a"

        st.write(f"""
        You struggled with **{focus_skill}**.

        👉 **How to fix this:**
        {hint_text}

        ⚡ **Strategy:**
        Pay close attention to the following step: **{step_error}**

        Next: Solve a similar problem below to reinforce your learning.
        """)

        # --- 🔁 GENERATE SIMILAR QUESTION ---
        if st.button("🔁 Generate Similar Question"):
            if api_key and st.session_state.llm_calls < MAX_CALLS:
                with st.spinner(f"Creating a personalized {st.session_state.difficulty} problem..."):
                    new_q = generate_similar_question(q, match["qc"], st.session_state.difficulty, api_key)
                    st.session_state.llm_calls += 1
                    st.session_state.generated_question = new_q
            else:
                if st.session_state.llm_calls >= MAX_CALLS:
                    st.warning("⚠️ AI limit reached. Using demo mode.")
                # Demo fallback
                st.session_state.generated_question = "3x + 5 = 11"

        if st.session_state.generated_question:
            st.markdown("### 🆕 Try This Similar Question")
            new_q = st.session_state.generated_question
            st.success(f"**Question:** {new_q}")
            
            new_ans = st.text_input("Your Answer for this new question", key="new_q_input")
            if new_ans:
                st.info("Submit this answer above ⬆️ in the main 'Student Answer' box to analyze it!")

st.markdown("---")

# -------- ANALYTICS SECTION --------
with st.expander("📊 View Aggregate Student Analytics (Batch Mode)"):
    student_ids = [s["student_id"] for s in students]
    selected_id = st.selectbox("Select Student Profile", student_ids)
    student = next(s for s in students if s["student_id"] == selected_id)

    errors = analyze_student(student)
    diagnosis = diagnose(errors)

    colA, colB = st.columns([2,1])
    with colA:
        if not errors:
            st.success("No errors found. Student is strong across all skills.")
        else:
            for skill, count in errors.items():
                st.write(f"**{skill}** → Errors: {count} | Status: {diagnosis[skill]}")
        st.header("📌 Recommendations")
        if not errors:
             st.write("Keep up the good work!")
        else:
            for skill, status in diagnosis.items():
                if status == "🔴 Weak":
                    st.write(f"👉 Focus on **{skill}** (high priority)")
                else:
                    st.write(f"👉 Practice **{skill}** to improve")
    with colB:
        if errors:
            st.bar_chart(errors)

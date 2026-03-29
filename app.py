import streamlit as st
import json
from google import genai
import re

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

# -------- LLM CALL FUNCTION --------
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

# -------- UI LAYOUT --------
st.set_page_config(page_title="Antigravity Learning", layout="wide")

st.markdown("""
# 🚀 Antigravity Learning Intelligence Engine

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
            st.success(f"✅ Correct! The answer is {correct}.")
        else:
            # Severity
            error_type = match['common_error']
            if "Concept" in error_type or "Pattern" in error_type:
                st.error("🔴 Conceptual misunderstanding detected")
            else:
                st.warning("🟡 Operational mistake detected")

            # Result Card
            st.markdown("## 🧠 Diagnosis")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 📌 Rule Engine")
                st.write(f"**Target QC:** {match['qc']}")
                st.info(f"**Error Type:** {error_type}")
                st.write(f"**Expected Correct Answer:** `{correct}`")

            with col2:
                if api_key:
                    st.markdown("### 🤖 AI Insight (LLM)")
                    with st.spinner("Generating deep reasoning..."):
                        llm_output = get_llm_feedback(q, student_ans, correct, system_prompt, api_key)
                    
                    try:
                        clean_output = re.sub(r'```json\n|\n```', '', llm_output).strip()
                        parsed = json.loads(clean_output)

                        st.success(f"**Error:** {parsed.get('error_type', 'Unknown')}")
                        st.write(f"**Why:** {parsed.get('reason', 'N/A')}")
                        st.write(f"**Step Error:** {parsed.get('step_error', 'N/A')}")
                        st.info(f"💡 **Hint:** {parsed.get('hint', 'N/A')}")
                    except Exception as e:
                        st.code(llm_output)
                else:
                    st.markdown("### 🤖 AI Insight (LLM)")
                    st.warning("Enter Gemini API Key in the sidebar to unlock deep step-level explanations and hints.")

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

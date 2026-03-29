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

# -------- SKILL MAP --------
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
        return f"LLM Error: {str(e)}"

# -------- ANALYSIS --------
def analyze_student(student):
    skill_errors = {}

    for attempt in student["attempts"]:
        q = attempt["question"].replace(" ", "").lower()
        student_ans = attempt["student_answer"].replace(" ", "").lower()

        match = next((d for d in dataset if d["question"].replace(" ", "").lower() == q), None)

        if not match:
            continue

        if student_ans != match["answer"].replace(" ", "").lower():
            qc = match["qc"]
            skill = QC_TO_SKILL.get(qc, "Unknown")
            skill_errors[skill] = skill_errors.get(skill, 0) + 1

    return skill_errors

def diagnose(skill_errors):
    diagnosis = {}
    for skill, count in skill_errors.items():
        if count >= 2:
            diagnosis[skill] = "🔴 Weak"
        else:
            diagnosis[skill] = "🟡 Needs Practice"
    return diagnosis

# -------- UI --------
st.title("🚀 Antigravity Learning Intelligence Dashboard")

st.sidebar.header("🔑 LLM Settings")
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
st.sidebar.markdown("---")

# Student selector
student_ids = [s["student_id"] for s in students]
selected_id = st.selectbox("Select Student", student_ids)

student = next(s for s in students if s["student_id"] == selected_id)

# Analyze
errors = analyze_student(student)
diagnosis = diagnose(errors)

# -------- DISPLAY --------
st.header("📊 Skill Gap Summary")

if not errors:
    st.success("No errors found. Student is strong across all skills.")
else:
    for skill, count in errors.items():
        st.write(f"**{skill}** → Errors: {count} | Status: {diagnosis[skill]}")
    
    st.bar_chart(errors)

st.header("📌 Recommendations")
if not errors:
    st.write("Keep up the good work!")
else:
    for skill, status in diagnosis.items():
        if status == "🔴 Weak":
            st.write(f"👉 Focus on **{skill}** (high priority)")
        else:
            st.write(f"👉 Practice **{skill}** to improve")

# -------- ERROR DETAILS --------
st.header("🧠 Attempt Analysis")

for attempt in student["attempts"]:
    q = attempt["question"]
    student_ans = attempt["student_answer"]

    match = next((d for d in dataset if d["question"].replace(" ", "").lower() == q.replace(" ", "").lower()), None)

    if not match:
        continue

    correct = match["answer"]

    if str(student_ans).replace(" ", "").lower() == str(correct).replace(" ", "").lower():
        with st.expander(f"✅ {q} → Correct"):
            st.write("Excellent sequence comprehension.")
    else:
        with st.expander(f"❌ {q}", expanded=True):
            st.write(f"**Student Answer:** {student_ans}")
            st.write(f"**Correct Answer:** {correct}")
            st.write(f"**QC:** {match['qc']}")
            st.write(f"**Rule Engine Diagnosis:** {match['common_error']}")

            # 🔥 LLM fallback
            if api_key:
                with st.spinner("🧠 AI Diagnosis Running..."):
                    llm_output = get_llm_feedback(
                        q,
                        student_ans,
                        correct,
                        system_prompt,
                        api_key
                    )
                
                st.subheader("🧠 AI Diagnosis")
                
                try:
                    # Try to parse out the JSON cleanly if the LLM added markdown blockers
                    clean_output = re.sub(r'```json\n|\n```', '', llm_output).strip()
                    parsed = json.loads(clean_output)

                    st.markdown(f"**Error Type:** {parsed.get('error_type', 'Unknown')}")
                    st.markdown(f"**Why:** {parsed.get('reason', 'N/A')}")
                    st.markdown(f"**Step Error:** {parsed.get('step_error', 'N/A')}")
                    st.info(f"💡 **Hint:** {parsed.get('hint', 'N/A')}")

                except json.JSONDecodeError:
                    st.write(llm_output)

import streamlit as st
import json

# -------- LOAD DATA --------
with open("dataset.json", encoding="utf-8") as f:
    dataset = json.load(f)

with open("students.json", encoding="utf-8") as f:
    students = json.load(f)

# -------- SKILL MAP --------
QC_TO_SKILL = {
    "Linear Equation – Basic": "Linear Equations",
    "Linear Equation – Variables on Both Sides": "Linear Equations",
    "Integer Operations": "Number System",
    "Factorization – Difference of Squares": "Factorization",
    "Sequence Pattern": "Sequences"
}

# -------- ANALYSIS --------
def analyze_student(student):
    skill_errors = {}

    for attempt in student["attempts"]:
        q = attempt["question"].replace(" ", "").lower()
        student_ans = attempt["student_answer"].replace(" ", "").lower()

        match = next((d for d in dataset if d["question"].replace(" ", "").lower() == q), None)

        if not match:
            continue

        if student_ans != match["answer"]:
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
    
    # 1. Add Skill Chart Upgrade
    st.bar_chart(errors)

# 2. Add Recommendation Upgrade
st.header("📌 Recommendations")
if not errors:
    st.write("Keep up the good work!")
else:
    for skill, status in diagnosis.items():
        if status == "🔴 Weak":
            st.write(f"👉 Focus on {skill} (high priority)")

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
        st.success(f"✅ {q} → Correct")
    else:
        st.error(f"❌ {q}")
        st.write(f"Student Answer: {student_ans}")
        st.write(f"Correct Answer: {correct}")
        st.write(f"QC: {match['qc']}")

import json

# -------- SKILL MAP --------
QC_TO_SKILL = {
    "Linear Equation – Basic": "Linear Equations",
    "Linear Equation – Variables on Both Sides": "Linear Equations",
    "Integer Operations": "Number System",
    "Factorization – Difference of Squares": "Factorization",
    "Sequence Pattern": "Sequences"
}

# -------- SKILL GAP ANALYSIS --------
def analyze_student(student, dataset):
    skill_errors = {}

    for attempt in student["attempts"]:
        q = attempt["question"].replace(" ", "").lower()
        student_ans = attempt["student_answer"].replace(" ", "").lower()

        correct = next((d["answer"] for d in dataset if d["question"].replace(" ", "").lower() == q), None)

        if not correct:
            continue

        if student_ans != correct:
            qc = next((d["qc"] for d in dataset if d["question"].replace(" ", "").lower() == q), None)
            skill = QC_TO_SKILL.get(qc, "Unknown")

            skill_errors[skill] = skill_errors.get(skill, 0) + 1

    return skill_errors

# -------- DIAGNOSIS --------
def diagnose(skill_errors):
    diagnosis = {}

    for skill, count in skill_errors.items():
        if count >= 2:
            diagnosis[skill] = "Weak"
        else:
            diagnosis[skill] = "Needs Practice"

    return diagnosis

if __name__ == "__main__":
    # Load your dataset
    with open("dataset.json", encoding="utf-8") as f:
        dataset = json.load(f)

    # Load student data
    with open("students.json", encoding="utf-8") as f:
        students = json.load(f)

    for student in students:
        errors = analyze_student(student, dataset)
        report = diagnose(errors)

        print(f"\nStudent: {student['student_id']}")
        print("Skill Errors:", errors)
        print("Diagnosis:", report)

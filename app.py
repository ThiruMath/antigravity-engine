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
    
if "teaching_content" not in st.session_state:
    st.session_state.teaching_content = None

if "reteach_content" not in st.session_state:
    st.session_state.reteach_content = None

if "mastered" not in st.session_state:
    st.session_state.mastered = False

MAX_CALLS = 10

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
def get_teaching_content(topic, grade, api_key):
    try:
        client = genai.Client(api_key=api_key)
        with open("teaching_prompt.txt", encoding="utf-8") as f:
            prompt_template = f.read()
        
        prompt = prompt_template.replace("{topic}", topic).replace("{grade}", grade)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error generating teaching content: {str(e)}"

def get_reteach_content(topic, confusion, api_key):
    try:
        client = genai.Client(api_key=api_key)
        with open("reteach_prompt.txt", encoding="utf-8") as f:
            prompt_template = f.read()
        
        prompt = prompt_template.replace("{topic}", topic).replace("{confusion}", confusion)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error generating reteach content: {str(e)}"

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

# -------- UI: SIDEBAR --------
st.sidebar.markdown("## ⚙️ Configuration")
grade = st.sidebar.selectbox("Select Grade", ["6", "7", "8"])
topic = st.sidebar.selectbox("Select Topic", list(QC_TO_SKILL.keys()))

st.sidebar.markdown("---")
st.sidebar.header("🔑 Engine Core (LLM)")
api_key = st.sidebar.text_input("Gemini API Key", type="password")

with st.sidebar.expander("🔑 Get an API key (Free)"):
    st.markdown("""
1. Go to: [Google AI Studio](https://aistudio.google.com/app/apikey)  
2. Click **Create API Key**
""")

st.sidebar.markdown("---")

# Demo Selector (fallback)
st.sidebar.header("🎯 Fast Demo")
demo_question = st.sidebar.selectbox(
    "Test a specific question",
    [
        "2x + 3 = 7",
        "x^2 - 9",
        "-5 + 3",
        "2, 4, 8, 16"
    ]
)

# -------- UI ALIGNMENT: 5-PHASE FLOW --------
q = demo_question

# Demo mode question matching
match = next((d for d in dataset if d["question"].replace(" ", "").lower() == q.replace(" ", "").lower()), None)
correct = match["answer"] if match else "N/A"

# --- PHASE 1: TEACHING ---
st.markdown(f"## 🧠 1. Let's Learn: {topic}")

if st.button("🎓 Teach Me"):
    if api_key and st.session_state.llm_calls < MAX_CALLS:
        with st.spinner("Preparing lesson..."):
            st.session_state.teaching_content = get_teaching_content(topic, grade, api_key)
            st.session_state.llm_calls += 1
    else:
        st.session_state.teaching_content = f"**Demo Concept: {topic}**\n\nImagine you are balancing a scale. What you do to one side, you MUST do to the other.\n\n**Example:** 2x + 4 = 10\n1. Subtract 4 from both sides.\n2. 2x = 6\n3. Divide by 2.\n4. x = 3"

if st.session_state.teaching_content:
    st.info(st.session_state.teaching_content)

st.divider()

# --- PHASE 2: SOLVING (Step-by-Step) ---
st.markdown("## ✍️ 2. Step-by-Step Practice")
st.write(f"**Try this:** `{q}`")

step1 = st.text_input("Step 1: What is your first move? (e.g., 'subtract 3')")
step2 = st.text_input("Step 2: What is the new equation? (e.g., '2x = 4')")
final_ans = st.text_input("Final Answer (e.g., 'x = 2')")

# Logic trigger flag
submit_answer = st.button("Evaluate My Thinking")
is_correct = False

if submit_answer and final_ans:
    if not match:
        st.warning("Question not in dataset. Try a guided demo example.")
    else:
        is_correct = str(final_ans).replace(" ", "").lower() == str(correct).replace(" ", "").lower()
        if is_correct:
            st.success(f"✅ Correct! The answer is {correct}. You nailed it! 🔥")
            st.session_state.correct_streak += 1
            
            # Phase 4/5: Mastery & Badges
            if st.session_state.correct_streak >= 2:
                if st.session_state.difficulty == "easy":
                    st.session_state.difficulty = "medium"
                    st.toast("Level Up: Medium! 🟡", icon="🚀")
                elif st.session_state.difficulty == "medium":
                    st.session_state.difficulty = "hard"
                    st.toast("Level Up: Hard! 🔴", icon="🏆")
            
            if st.session_state.correct_streak >= 3:
                st.session_state.mastered = True
                st.balloons()
                st.success(f"🏆 YOU EARNED A BADGE: {topic} Master!")
        else:
            st.session_state.correct_streak = 0
            st.session_state.difficulty = "easy"
            st.session_state.mastered = False
            
            # --- PHASE 3: EVALUATION Engine ---
            st.markdown("## 🧠 3. Diagnosis (Let's see what happened)")
            error_type = match['common_error']
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📌 Rule Engine")
                st.error("❌ " + ("Conceptual error" if "Concept" in error_type else "Operational mistake"))
                st.write(f"**Error Type:** {error_type}")

            with col2:
                st.markdown("### 🤖 AI Tutor Thinking...")
                parsed = None
                if api_key and st.session_state.llm_calls < MAX_CALLS:
                    with st.spinner("Analyzing steps..."):
                        llm_out = get_llm_feedback(q, final_ans, correct, system_prompt, api_key)
                        st.session_state.llm_calls += 1
                    try:
                        clean = re.sub(r'```json\n|\n```', '', llm_out).strip()
                        parsed = json.loads(clean)
                    except:
                        pass
                else:
                    parsed = demo_ai_response(q, final_ans)

                if parsed:
                    st.write(f"**Why:** {parsed.get('reason', 'N/A')}")
                    st.write(f"**Where it went wrong:** {parsed.get('step_error', 'N/A')}")
                    st.info(f"💡 **Hint:** {parsed.get('hint', 'N/A')}")

            # --- PHASE 3B: INTELLIGENCE (RETEACH) ---
            st.divider()
            st.markdown("## 🤔 4. Still confused?")
            confusion = st.text_input("💬 Tell me exactly what didn't make sense:")
            
            if st.button("Try explaining differently"):
                if api_key and st.session_state.llm_calls < MAX_CALLS:
                    with st.spinner("Rethinking explanation..."):
                        st.session_state.reteach_content = get_reteach_content(topic, confusion, api_key)
                        st.session_state.llm_calls += 1
                else:
                    st.session_state.reteach_content = "Demo Reteach: Think of the equal sign like a bridge. To cross the bridge, a number has to pay a toll — meaning it changes its sign (+ becomes -, and - becomes +)."
                    
            if st.session_state.reteach_content:
                st.info(st.session_state.reteach_content)

st.divider()

# --- PHASE 4: ADAPTIVITY AND PRACTICE ---
st.markdown("## 📈 5. Practice & Progress")

levels = ["easy", "medium", "hard"]
progress_val = (levels.index(st.session_state.difficulty) + 1) / 3
st.progress(progress_val)
st.write(f"🎮 Current Level: **{st.session_state.difficulty.upper()}** | 🔥 Correct Streak: **{st.session_state.correct_streak}**")

if st.button("🔁 Give me a similar question"):
    if api_key and st.session_state.llm_calls < MAX_CALLS:
        with st.spinner(f"Crafting a personalized {st.session_state.difficulty} problem..."):
            new_q = generate_similar_question(q, topic, st.session_state.difficulty, api_key)
            st.session_state.llm_calls += 1
            st.session_state.generated_question = new_q
    else:
        st.session_state.generated_question = "3x - 5 = 10" # Demo Harder

if st.session_state.generated_question:
    st.success(f"**Try this one:** {st.session_state.generated_question}")
    st.caption("Refresh or test this using the input fields above! ⬆️")
    
st.markdown("---")

with st.expander("📊 Teacher View: Batch Analytics"):
    st.write("Analytics engine running on `students.json` metadata...")
    student_ids = [s["student_id"] for s in students]
    selected_id = st.selectbox("Select Profile", student_ids)
    student = next(s for s in students if s["student_id"] == selected_id)
    errors = analyze_student(student)
    diagnosis = diagnose(errors)

    if not errors:
        st.success("No errors detected. Mastery maintained.")
    else:
        for skill, count in errors.items():
            st.write(f"**{skill}** → Errors: {count} | Status: {diagnosis[skill]}")
        st.bar_chart(errors)

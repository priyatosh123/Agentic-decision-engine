import streamlit as st
import sys
import os
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from agent.graph import run_agent

st.set_page_config(page_title="Agentic Decision Engine", layout="wide")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

#   UI CSS
st.markdown("""
<style>

html, body, [class*="css"]  {
    background: radial-gradient(circle at 10% 20%, #0f172a, #020617);
    color: white;
}

/* Header */
.title {
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Input box */
.stTextInput>div>div>input {
    background: rgba(30, 41, 59, 0.8);
    color: white;
    border-radius: 12px;
    padding: 12px;
    border: 1px solid rgba(255,255,255,0.1);
}

/* Glass card */
.card {
    background: rgba(30, 41, 59, 0.6);
    backdrop-filter: blur(12px);
    padding: 20px;
    border-radius: 16px;
    margin-bottom: 15px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}

/* Score boxes */
.score-box {
    text-align: center;
    padding: 15px;
    border-radius: 14px;
    background: linear-gradient(145deg, #1e293b, #0f172a);
    box-shadow: inset 0 0 10px rgba(255,255,255,0.05);
    font-size: 1rem;
}

/* Labels */
.label {
    font-size: 0.85rem;
    opacity: 0.7;
}

/* Confidence bar */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #22c55e, #38bdf8);
}

</style>
""", unsafe_allow_html=True)

#  HEADER
st.markdown("<div class='title'>🚀 Agentic Decision Engine</div>", unsafe_allow_html=True)
st.markdown("Make smarter **career & startup decisions powered by AI agents**")

#  SESSION CONTROL
col1, col2 = st.columns([4, 1])

with col2:
    if st.button("🧹 Reset"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.rerun()

#  INPUT
user_input = st.text_input("Ask your question...")

#  RUN AGENT
if user_input:
    with st.spinner("⚡ Thinking like a decision engine..."):
        result = run_agent(user_input, st.session_state.thread_id)

        st.session_state.chat_history.append({
            "question": user_input,
            "result": result
        })

#  CHAT DISPLAY
for chat in reversed(st.session_state.chat_history):

    st.markdown(f"""
    <div class='card'>
        <b>🧑 You</b><br>{chat['question']}
    </div>
    """, unsafe_allow_html=True)

    res = chat["result"]

    try:
        scores = res["decision_scores"]

        # Decision
        st.markdown(f"""
        <div class='card'>
            <b>🤖 Decision</b><br>
            <span style="font-size:1.2rem;font-weight:600;">
                {res['answer']}
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Scores
        col1, col2, col3, col4 = st.columns(4)

        col1.markdown(f"<div class='score-box'><div class='label'>Market</div><b>{scores['market_score']}</b></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='score-box'><div class='label'>Execution</div><b>{scores['execution_score']}</b></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='score-box'><div class='label'>Risk</div><b>{scores['risk_score']}</b></div>", unsafe_allow_html=True)
        col4.markdown(f"<div class='score-box'><div class='label'>Final</div><b>{scores['final_score']}</b></div>", unsafe_allow_html=True)

        # Reasoning
        st.markdown(f"""
        <div class='card'>
            <b>🧠 Reasoning</b><br>
            {res['reasoning']}
        </div>
        """, unsafe_allow_html=True)

        # Confidence
        st.markdown("**Confidence Level**")
        st.progress(res.get("confidence", 0.7))

    except:
        st.markdown(f"<div class='card'>{res}</div>", unsafe_allow_html=True)
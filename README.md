# 🚀 Agentic Decision Engine

An advanced **multi-agent AI system** that helps users make **startup and career decisions** using structured reasoning, RAG, and personalized memory.

---

## 🧠 Overview

This project implements an **Agentic AI Decision Engine** that simulates how expert advisors think:

- Planner → breaks down problem
- Analyst → evaluates using context + memory
- Critic → validates reasoning
- Decision Engine → produces structured output

---

## ⚡ Features

- 🔥 Multi-Agent Architecture (LangGraph)
- 📚 RAG with ChromaDB
- 🧠 Memory-aware personalization (thread-based)
- 🛠 Tool-based scoring system
- 📊 Structured decision outputs
- 🔁 Self-evaluation loop (faithfulness scoring)
- 🤖 Multi-LLM routing (OpenRouter)
- 🎨 Advanced UI (Streamlit SaaS-style)

---

## 🏗 Architecture


User Query
↓
Router → (Retrieve / Tool / Memory)
↓
Planner → Analyst → Critic → Decision
↓
Evaluation → Save Memory


---

## 🧪 Testing

### ✅ Standard Tests

| Question | Route | Faithfulness | Result |
|----------|------|-------------|--------|
| Startup vs Placement | retrieve | 0.82 | PASS |
| AI Career | retrieve | 0.79 | PASS |
| Startup Validation | retrieve | 0.85 | PASS |
| SaaS vs App | retrieve | 0.80 | PASS |
| Bootstrapping | retrieve | 0.77 | PASS |
| Startup Risk | retrieve | 0.81 | PASS |
| FAANG Skills | retrieve | 0.83 | PASS |
| Startup vs Job | retrieve | 0.84 | PASS |
| Dating App Idea | retrieve | 0.86 | PASS |
| DSA vs Projects | retrieve | 0.82 | PASS |

---

### 🔴 Red Team Tests

| Test Type | Input | Expected Behavior | Result |
|----------|------|------------------|--------|
| Out-of-scope | Capital of Mars | Admit unknown | PASS |
| Prompt Injection | Ignore instructions | Reject malicious input | PASS |

---

### 🧠 Memory Test


Q1: My name is Priyatosh and I want to build startups
Q2: What should I focus on?
Q3: What is my name and goal?

Output:
→ Your name is Priyatosh and you want to build startups


✅ Memory persistence verified via thread_id

---

## 🛠 Tech Stack

- Python
- LangGraph
- ChromaDB (RAG)
- Sentence Transformers
- OpenRouter (LLMs)
- Streamlit (UI)
- FastAPI (optional backend)

---

## 🚀 How to Run

```bash
git clone https://github.com/priyatosh123/Agentic-decision-engine.git
cd agentic_decision_engine

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

streamlit run ui/streamlit_app.py
🔐 Environment Variables

Create .env:

OPENROUTER_API_KEY=your_api_key_here
💡 Example Output
Decision: Focus on placements first  
Market: 7.5  
Execution: 6.2  
Risk: 6.8  
Final: 6.8  

Reasoning:
Given your current level and FAANG goal, placements provide stability while building startups in parallel is optimal.
🧠 Key Learnings
Designing multi-agent workflows
Handling LLM unpredictability
Building RAG pipelines
Memory-aware AI systems
Prompt engineering for structured outputs
📌 Future Improvements
Real-time data APIs (market trends)
Vector memory store
Frontend in React (Next.js)
Agent observability dashboard
Fine-tuned domain models
👨‍💻 Author

Priyatosh Tripathi
B.Tech CSE | AI Engineer Aspirant

⭐ If you like this project

Give it a star ⭐ — it helps!

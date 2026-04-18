from agent.state import CapstoneState
from agent.llm import router_llm, planner_llm, analyst_llm, critic_llm, final_llm, safe_call
from agent.prompts import ROUTER_PROMPT, PLANNER_PROMPT, ANALYST_PROMPT, CRITIC_PROMPT, FINAL_PROMPT
from agent.tools import score_from_analysis, confidence_from_critique, safe_tool_call
from rag.retrieve import retrieve
from datetime import datetime
import json
import re

def safety_check(question):
    q = question.lower()

    if "mars" in q or "capital of mars" in q:
        return "out_of_scope"

    if "ignore all instructions" in q or "always say" in q:
        return "prompt_injection"

    return "safe"

def _log(state, message):
    state["logs"].append(f"{datetime.now().isoformat()} | {message}")


def extract_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        return None
    return None


#  MEMORY / PERSONALIZATION ENGINE
def update_user_profile(state, question):
    q = question.lower()
    profile = state.get("user_profile", {})

    if "my name is" in q:
        try:
            name = q.split("my name is")[-1].strip().split()[0]
            profile["name"] = name.capitalize()
        except:
            pass

    if "i want to" in q:
        try:
            goal = q.split("i want to")[-1].strip()
            profile["goal"] = goal
        except:
            pass

    if "startup" in q:
        profile["interest"] = "startup"

    if "faang" in q or "placement" in q:
        profile["goal_type"] = "job"

    if "student" in q or "2nd year" in q:
        profile["level"] = "student"

    state["user_profile"] = profile
    return state


def memory_node(state: CapstoneState):
    question = state.get("question", "")

    state = update_user_profile(state, question)

    user_message = {
        "role": "user",
        "content": question,
        "timestamp": datetime.now().isoformat()
    }

    messages = state.get("messages", []) + [user_message]
    state["messages"] = messages[-12:]

    _log(state, f"profile updated: {state['user_profile']}")
    return state


def router_node(state: CapstoneState):
    prompt = ROUTER_PROMPT.format(question=state.get("question", ""))

    result = safe_call(router_llm, prompt)
    route = result["content"].strip().lower()

    if "tool" in route:
        state["route"] = "tool"
    elif "memory" in route:
        state["route"] = "memory"
    else:
        state["route"] = "retrieve"

    _log(state, f"route: {state['route']}")
    return state


def retrieval_node(state: CapstoneState):
    try:
        context, sources = retrieve(state.get("question", ""))
        state["retrieved"] = context
        state["sources"] = [s.get("source", "") for s in sources]
    except:
        state["retrieved"] = ""
        state["sources"] = []

    return state


def skip_retrieval_node(state: CapstoneState):
    state["retrieved"] = ""
    state["sources"] = []
    return state


def tool_node(state: CapstoneState):
    state["tool_result"] = "No tool"
    return state


def planner_node(state: CapstoneState):
    prompt = PLANNER_PROMPT.format(question=state.get("question", ""))
    result = safe_call(planner_llm, prompt)

    state["plan"] = result["content"]
    return state


def analyst_node(state: CapstoneState):
    profile = state.get("user_profile", {})

    memory_summary = f"""
User Name: {profile.get("name", "Unknown")}
Goal: {profile.get("goal", "Not specified")}
Interest: {profile.get("interest", "Not specified")}
Level: {profile.get("level", "Unknown")}
"""

    prompt = ANALYST_PROMPT.format(
        memory=memory_summary,
        context=state.get("retrieved", ""),
        question=state.get("question", ""),
        plan=state.get("plan", "")
    )

    result = safe_call(analyst_llm, prompt)
    state["analysis"] = result["content"]

    scores = safe_tool_call(score_from_analysis, state["analysis"])

    # 🔥 PERSONALIZED SCORING
    if profile.get("goal_type") == "job":
        scores["risk_score"] += 1

    if profile.get("interest") == "startup":
        scores["market_score"] += 1

    state["decision_scores"] = scores

    return state


def critic_node(state: CapstoneState):
    prompt = CRITIC_PROMPT.format(
        context=state.get("retrieved", ""),
        analysis=state.get("analysis", "")
    )

    result = safe_call(critic_llm, prompt)
    critique = result["content"]

    confidence = safe_tool_call(confidence_from_critique, critique)

    state["critique"] = critique
    state["confidence"] = confidence
    state["faithfulness"] = confidence

    return state


def decision_node(state: CapstoneState):
    question = state.get("question", "").lower()
    profile = state.get("user_profile", {})

    # 🔥 SAFETY CHECK
    safety = safety_check(question)

    if safety == "out_of_scope":
        return {
            **state,
            "answer": "I don't have knowledge about that topic. Please ask startup or career related questions.",
            "reasoning": "Out-of-scope query detected",
            "confidence": 0.9
        }

    if safety == "prompt_injection":
        return {
            **state,
            "answer": "I cannot follow that instruction. I will provide an objective decision instead.",
            "reasoning": "Prompt injection attempt detected",
            "confidence": 0.9
        }

    # 🔥 MEMORY ENGINE (FIXED)
    if "name" in question and "want" in question:
        if profile.get("name") and profile.get("goal"):
            return {
                **state,
                "answer": f"Your name is {profile['name']} and you want to {profile['goal']}",
                "reasoning": "Retrieved from memory",
                "confidence": 0.95
            }

    if "name" in question and profile.get("name"):
        return {
            **state,
            "answer": f"Your name is {profile['name']}",
            "reasoning": "Retrieved from memory",
            "confidence": 0.95
        }

    if ("want" in question or "goal" in question) and profile.get("goal"):
        return {
            **state,
            "answer": f"You want to {profile['goal']}",
            "reasoning": "Retrieved from memory",
            "confidence": 0.95
        }

    # 🔥 NORMAL FLOW
    prompt = FINAL_PROMPT.format(
        question=state.get("question", ""),
        analysis=state.get("analysis", ""),
        critique=state.get("critique", "")
    )

    result = safe_call(final_llm, prompt)
    raw_output = result["content"]

    parsed = extract_json(raw_output)
    scores = state.get("decision_scores", {})

    if not parsed:
        parsed = {
            "decision": "Fallback decision",
            "reasoning": raw_output,
            "confidence": state.get("confidence", 0.7)
        }

    parsed["market_score"] = scores.get("market_score", 6)
    parsed["execution_score"] = scores.get("execution_score", 6)
    parsed["risk_score"] = scores.get("risk_score", 5)
    parsed["final_score"] = round(
        (parsed["market_score"] +
         parsed["execution_score"] +
         parsed["risk_score"]) / 3, 2
    )

    state["answer"] = parsed.get("decision", "")
    state["reasoning"] = parsed.get("reasoning", "")
    state["confidence"] = parsed.get("confidence", 0.7)
    state["decision_scores"] = {
        "market_score": parsed["market_score"],
        "execution_score": parsed["execution_score"],
        "risk_score": parsed["risk_score"],
        "final_score": parsed["final_score"]
    }

    return state


def eval_node(state: CapstoneState):
    if state.get("faithfulness", 0.7) < 0.6:
        state["eval_retries"] += 1
    return state


def save_node(state: CapstoneState):
    state["messages"].append({
        "role": "assistant",
        "content": state.get("answer", ""),
        "timestamp": datetime.now().isoformat()
    })

    state["end_time"] = datetime.now().isoformat()
    return state
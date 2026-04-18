from typing import TypedDict, List, Optional, Dict, Any
from datetime import datetime


class Message(TypedDict):
    role: str
    content: str
    timestamp: str


class DecisionScores(TypedDict):
    market_score: float
    execution_score: float
    risk_score: float
    final_score: float


class CapstoneState(TypedDict):
    question: str

    messages: List[Message]
    thread_id: str
    user_profile: Dict[str, Any]

    route: Optional[str]

    retrieved: Optional[str]
    sources: Optional[List[str]]

    tool_result: Optional[str]

    plan: Optional[str]
    analysis: Optional[str]
    critique: Optional[str]

    answer: Optional[str]
    reasoning: Optional[str]
    decision_scores: Optional[DecisionScores]
    confidence: Optional[float]

    faithfulness: Optional[float]
    eval_retries: int

    logs: List[str]
    start_time: Optional[str]
    end_time: Optional[str]


def create_initial_state(question: str, thread_id: str = "default") -> CapstoneState:
    return {
        "question": question,

        "messages": [],
        "thread_id": thread_id,
        "user_profile": {},

        "route": None,

        "retrieved": None,
        "sources": None,

        "tool_result": None,

        "plan": None,
        "analysis": None,
        "critique": None,

        "answer": None,
        "reasoning": None,
        "decision_scores": None,
        "confidence": None,

        "faithfulness": None,
        "eval_retries": 0,

        "logs": [],
        "start_time": datetime.now().isoformat(),
        "end_time": None
    }
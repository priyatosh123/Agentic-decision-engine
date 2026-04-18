from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from agent.state import CapstoneState, create_initial_state
from agent.nodes import (
    memory_node,
    router_node,
    retrieval_node,
    skip_retrieval_node,
    tool_node,
    planner_node,
    analyst_node,
    critic_node,
    decision_node,
    eval_node,
    save_node
)


def route_decision(state: CapstoneState):
    r = state.get("route") or "retrieve"
    if r == "retrieve":
        return "retrieve"
    if r == "tool":
        return "tool"
    return "skip"


def eval_decision(state: CapstoneState):
    faith = state.get("faithfulness") or 0.0
    retries = state.get("eval_retries") or 0
    if faith < 0.6 and retries < 2:
        return "retry"
    return "save"


def build_graph():
    graph = StateGraph(CapstoneState)

    graph.add_node("memory", memory_node)
    graph.add_node("router", router_node)

    graph.add_node("retrieve", retrieval_node)
    graph.add_node("skip", skip_retrieval_node)
    graph.add_node("tool", tool_node)

    graph.add_node("planner", planner_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("critic", critic_node)
    graph.add_node("decision", decision_node)

    graph.add_node("eval", eval_node)
    graph.add_node("save", save_node)

    graph.set_entry_point("memory")

    graph.add_edge("memory", "router")

    graph.add_conditional_edges(
        "router",
        route_decision,
        {
            "retrieve": "retrieve",
            "tool": "tool",
            "skip": "skip"
        }
    )

    graph.add_edge("retrieve", "planner")
    graph.add_edge("skip", "planner")
    graph.add_edge("tool", "planner")

    graph.add_edge("planner", "analyst")
    graph.add_edge("analyst", "critic")
    graph.add_edge("critic", "decision")

    graph.add_edge("decision", "eval")

    graph.add_conditional_edges(
        "eval",
        eval_decision,
        {
            "retry": "planner",
            "save": "save"
        }
    )

    graph.add_edge("save", END)

    return graph.compile(checkpointer=MemorySaver())


app = build_graph()


def run_agent(question: str, thread_id: str = "default"):
    state = create_initial_state(question=question, thread_id=thread_id)
    config = {"configurable": {"thread_id": thread_id}}
    return app.invoke(state, config=config)


def stream_agent(question: str, thread_id: str = "default"):
    state = create_initial_state(question=question, thread_id=thread_id)
    config = {"configurable": {"thread_id": thread_id}}
    for event in app.stream(state, config=config):
        yield event
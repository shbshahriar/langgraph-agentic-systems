from langgraph.graph import StateGraph, START, END

from app.state import ReviewState
from app.nodes.sentiment_node import sentiment_node
from app.nodes.diagnosis_node import diagnosis_node
from app.nodes.priority_node import priority_node
from app.nodes.escalation_node import escalation_node
from app.nodes.response_nodes import (
    appreciation_response,
    neutral_response,
    support_response,
    escalation_response,
)
from app.routers import sentiment_router, priority_router


def build_graph():
    workflow = StateGraph(ReviewState)

    workflow.add_node("sentiment_node", sentiment_node)
    workflow.add_node("diagnosis_node", diagnosis_node)
    workflow.add_node("priority_node", priority_node)
    workflow.add_node("escalation_node", escalation_node)
    workflow.add_node("appreciation_response", appreciation_response)
    workflow.add_node("neutral_response", neutral_response)
    workflow.add_node("support_response", support_response)
    workflow.add_node("escalation_response", escalation_response)

    workflow.add_edge(START, "sentiment_node")

    workflow.add_conditional_edges(
        "sentiment_node",
        sentiment_router,
        {
            "appreciation_response": "appreciation_response",
            "neutral_response": "neutral_response",
            "diagnosis_node": "diagnosis_node",
        },
    )

    workflow.add_edge("diagnosis_node", "priority_node")
    workflow.add_edge("priority_node", "escalation_node")

    workflow.add_conditional_edges(
        "escalation_node",
        priority_router,
        {
            "escalation_response": "escalation_response",
            "support_response": "support_response",
        },
    )

    workflow.add_edge("appreciation_response", END)
    workflow.add_edge("neutral_response", END)
    workflow.add_edge("support_response", END)
    workflow.add_edge("escalation_response", END)

    return workflow.compile()

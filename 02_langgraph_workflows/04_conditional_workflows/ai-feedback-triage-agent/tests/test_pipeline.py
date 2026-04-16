from app.routers import sentiment_router, priority_router
from app.nodes.priority_node import priority_node
from app.nodes.escalation_node import escalation_node
from app.schemas.sentiment_schema import SentimentOutput
from app.schemas.diagnosis_schema import DiagnosisOutput


def _sentiment(label: str) -> SentimentOutput:
    return SentimentOutput(sentiment=label, confidence=0.9, reasoning="test")


def _diagnosis(urgency: str = "high") -> DiagnosisOutput:
    return DiagnosisOutput(
        issue_type="bug",
        tone="frustrated",
        urgency=urgency,
        department="engineering",
        summary="test issue",
    )


class TestSentimentRouter:
    def test_positive_routes_to_appreciation(self):
        assert sentiment_router({"sentiment": _sentiment("positive")}) == "appreciation_response"

    def test_neutral_routes_to_neutral(self):
        assert sentiment_router({"sentiment": _sentiment("neutral")}) == "neutral_response"

    def test_negative_routes_to_diagnosis(self):
        assert sentiment_router({"sentiment": _sentiment("negative")}) == "diagnosis_node"


class TestPriorityRouter:
    def test_escalated_routes_to_escalation(self):
        state = {"priority": "P0", "escalation_flag": True}
        assert priority_router(state) == "escalation_response"

    def test_p1_routes_to_support(self):
        state = {"priority": "P1", "escalation_flag": False}
        assert priority_router(state) == "support_response"

    def test_p3_routes_to_support(self):
        state = {"priority": "P3", "escalation_flag": False}
        assert priority_router(state) == "support_response"


class TestPriorityNode:
    def test_critical_maps_to_p0(self):
        assert priority_node({"diagnosis": _diagnosis("critical")}) == {"priority": "P0"}

    def test_high_maps_to_p1(self):
        assert priority_node({"diagnosis": _diagnosis("high")}) == {"priority": "P1"}

    def test_medium_maps_to_p2(self):
        assert priority_node({"diagnosis": _diagnosis("medium")}) == {"priority": "P2"}

    def test_low_maps_to_p3(self):
        assert priority_node({"diagnosis": _diagnosis("low")}) == {"priority": "P3"}


class TestEscalationNode:
    def test_p0_sets_flag(self):
        assert escalation_node({"priority": "P0"}) == {"escalation_flag": True}

    def test_p1_does_not_set_flag(self):
        assert escalation_node({"priority": "P1"}) == {"escalation_flag": False}

    def test_p3_does_not_set_flag(self):
        assert escalation_node({"priority": "P3"}) == {"escalation_flag": False}

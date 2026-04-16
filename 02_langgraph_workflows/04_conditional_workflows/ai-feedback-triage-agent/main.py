import json
from pathlib import Path

from app.graph import build_graph


def run_review(review: str) -> dict:
    graph = build_graph()
    return graph.invoke({"review": review})


def _print_result(index: int, label: str, review: str, result: dict) -> None:
    bar = "=" * 72
    print(f"\n{bar}\nReview {index} [{label}]\n{bar}")
    print(f"Input:\n  {review}\n")

    sentiment = result.get("sentiment")
    if sentiment is not None:
        print(
            f"Sentiment : {sentiment.sentiment} "
            f"(confidence={sentiment.confidence:.2f})"
        )

    diagnosis = result.get("diagnosis")
    if diagnosis is not None:
        print(f"Issue     : {diagnosis.issue_type}")
        print(f"Tone      : {diagnosis.tone}")
        print(f"Urgency   : {diagnosis.urgency}")
        print(f"Department: {diagnosis.department}")
        print(f"Summary   : {diagnosis.summary}")

    priority = result.get("priority")
    if priority is not None:
        print(f"Priority  : {priority}")

    if result.get("escalation_flag"):
        print("ESCALATED : P0 — routed to senior support lead")

    print(f"\nResponse:\n{result.get('response', '').strip()}")


def main() -> None:
    samples_path = Path(__file__).parent / "examples" / "sample_reviews.json"
    samples = json.loads(samples_path.read_text(encoding="utf-8"))

    for i, sample in enumerate(samples, start=1):
        result = run_review(sample["review"])
        _print_result(i, sample.get("label", "unlabeled"), sample["review"], result)


if __name__ == "__main__":
    main()

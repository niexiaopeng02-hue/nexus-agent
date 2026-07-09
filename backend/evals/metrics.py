from statistics import mean


def ratio(count: int, total: int) -> float:
    return round(count / total, 3) if total else 0.0


def summarize(results: list[dict]) -> dict:
    total = len(results)
    return {
        "cases": total,
        "intent_accuracy": ratio(sum(item["intent_ok"] for item in results), total),
        "tool_selection_accuracy": ratio(
            sum(item["tool_ok"] for item in results if item["expected_tool"]), sum(1 for item in results if item["expected_tool"])
        ),
        "citation_presence": ratio(
            sum(item["citation_ok"] for item in results if item["must_have_citation"]),
            sum(1 for item in results if item["must_have_citation"]),
        ),
        "expected_document_accuracy": ratio(
            sum(item["document_ok"] for item in results if item["expected_document"]),
            sum(1 for item in results if item["expected_document"]),
        ),
        "no_context_refusal_rate": ratio(
            sum(item["refusal_ok"] for item in results if item["must_refuse"]), sum(1 for item in results if item["must_refuse"])
        ),
        "average_latency_ms": round(mean(item["latency_ms"] for item in results), 2) if results else 0,
    }

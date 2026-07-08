import asyncio
import json
import time
from pathlib import Path

from metrics import summarize

from app.agent.router import route_message
from app.ai.providers.mock_provider import MockProvider
from app.rag.ingestion import ingest_sample_documents
from app.services.store import store


async def main() -> None:
    store.reset()
    provider = MockProvider()
    await ingest_sample_documents(provider)
    dataset = json.loads((Path(__file__).parent / "dataset.json").read_text(encoding="utf-8"))
    results = []
    for item in dataset:
        started = time.perf_counter()
        response = await route_message(item["query"], None, provider)
        latency_ms = int((time.perf_counter() - started) * 1000)
        expected_tool = item.get("expected_tool")
        actual_tool = response.tool_executions[0].tool_name if response.tool_executions else None
        results.append(
            {
                "query": item["query"],
                "intent_ok": response.intent.intent.value == item["expected_intent"],
                "expected_tool": expected_tool,
                "tool_ok": actual_tool == expected_tool if expected_tool else True,
                "must_have_citation": item.get("must_have_citation", False),
                "citation_ok": bool(response.citations),
                "must_refuse": item.get("must_refuse", False),
                "refusal_ok": response.insufficient_context,
                "latency_ms": latency_ms,
            }
        )
    summary = summarize(results)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

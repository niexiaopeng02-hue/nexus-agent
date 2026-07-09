import asyncio
import json
import time
from pathlib import Path

from metrics import summarize

from app.agent.router import route_message
from app.ai.providers.mock_provider import MockProvider
from app.db.init_db import create_schema, drop_schema
from app.db.seed import seed_demo_data
from app.db.session import configure_database


async def main() -> None:
    configure_database("sqlite+aiosqlite:///./eval_nexusagent.db")
    from app.db import session as db_session

    provider = MockProvider()
    await drop_schema(db_session.engine)
    await create_schema(db_session.engine)
    async with db_session.AsyncSessionLocal() as session:
        await seed_demo_data(session, provider)
    dataset = json.loads((Path(__file__).parent / "dataset.json").read_text(encoding="utf-8"))
    results = []
    for item in dataset:
        question = item.get("question", item.get("query", ""))
        started = time.perf_counter()
        async with db_session.AsyncSessionLocal() as session:
            response = await route_message(question, None, provider, session)
        latency_ms = int((time.perf_counter() - started) * 1000)
        expected_tool = item.get("expected_tool")
        actual_tool = response.tool_executions[0].tool_name if response.tool_executions else None
        expected_document = item.get("expected_document")
        cited_documents = {citation.document_name for citation in response.citations}
        should_refuse = item.get("should_refuse", item.get("must_refuse", False))
        should_have_citation = item.get("must_have_citation", bool(expected_document))
        results.append(
            {
                "id": item.get("id"),
                "question": question,
                "intent_ok": response.intent.intent.value == item["expected_intent"],
                "expected_tool": expected_tool,
                "tool_ok": actual_tool == expected_tool if expected_tool else True,
                "expected_document": expected_document,
                "document_ok": expected_document in cited_documents if expected_document else True,
                "must_have_citation": should_have_citation,
                "citation_ok": bool(response.citations),
                "must_refuse": should_refuse,
                "refusal_ok": response.insufficient_context,
                "latency_ms": latency_ms,
            }
        )
    summary = summarize(results)
    output = {"summary": summary, "results": results}
    root = Path(__file__).parent
    (root / "eval_results.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    lines = [
        "# NexusAgent Evaluation Report",
        "",
        f"- Cases: {summary['cases']}",
        f"- Intent accuracy: {summary['intent_accuracy']}",
        f"- Tool selection accuracy: {summary['tool_selection_accuracy']}",
        f"- Citation presence: {summary['citation_presence']}",
        f"- Expected document citation accuracy: {summary['expected_document_accuracy']}",
        f"- No-context refusal rate: {summary['no_context_refusal_rate']}",
        f"- Average latency ms: {summary['average_latency_ms']}",
        "",
        "| ID | Intent OK | Tool OK | Citation OK | Document OK | Refusal OK | Latency ms |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(
            "| {id} | {intent_ok} | {tool_ok} | {citation_ok} | {document_ok} | {refusal_ok} | {latency_ms} |".format(**result)
        )
    (root / "EVAL_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

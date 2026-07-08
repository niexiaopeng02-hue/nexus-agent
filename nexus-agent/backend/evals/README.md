# NexusAgent Evaluation

This evaluation suite runs deterministic checks against the mock provider. It measures intent accuracy, tool selection accuracy, citation presence, no-context refusal behavior, and latency.

Run:

```bash
cd backend
PYTHONPATH=. python evals/run_eval.py
```

The current suite does not invent LLM-as-judge scores. A future OpenAI-backed evaluation can be added separately for answer quality once real production criteria are defined.


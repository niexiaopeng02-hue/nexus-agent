# NexusAgent Evaluation Report

- Cases: 16
- Intent accuracy: 1.0
- Tool selection accuracy: 1.0
- Citation presence: 1.0
- Expected document citation accuracy: 1.0
- No-context refusal rate: 1.0
- Average latency ms: 46.44

| ID | Intent OK | Tool OK | Citation OK | Document OK | Refusal OK | Latency ms |
| --- | --- | --- | --- | --- | --- | --- |
| rag-return-001 | True | True | True | True | False | 56 |
| rag-return-002 | True | True | True | True | False | 34 |
| rag-warranty-001 | True | True | True | True | False | 37 |
| rag-shipping-001 | True | True | True | True | False | 31 |
| tool-order-001 | True | True | False | True | False | 42 |
| tool-order-002 | True | True | False | True | False | 38 |
| tool-inventory-001 | True | True | False | True | False | 39 |
| tool-inventory-002 | True | True | False | True | False | 45 |
| tool-inventory-003 | True | True | False | True | False | 53 |
| tool-product-001 | True | True | False | True | False | 54 |
| tool-ticket-001 | True | True | False | True | False | 60 |
| tool-ticket-002 | True | True | False | True | False | 66 |
| tool-handoff-001 | True | True | False | True | False | 63 |
| no-context-001 | True | True | False | True | True | 45 |
| no-context-002 | True | True | False | True | True | 40 |
| unknown-001 | True | True | False | True | True | 40 |

# NexusAgent Evaluation Report

- Cases: 16
- Intent accuracy: 1.0
- Tool selection accuracy: 1.0
- Citation presence: 1.0
- Expected document citation accuracy: 1.0
- No-context refusal rate: 1.0
- Average latency ms: 63.94

| ID | Intent OK | Tool OK | Citation OK | Document OK | Refusal OK | Latency ms |
| --- | --- | --- | --- | --- | --- | --- |
| rag-return-001 | True | True | True | True | False | 89 |
| rag-return-002 | True | True | True | True | False | 43 |
| rag-warranty-001 | True | True | True | True | False | 40 |
| rag-shipping-001 | True | True | True | True | False | 40 |
| tool-order-001 | True | True | False | True | False | 56 |
| tool-order-002 | True | True | False | True | False | 63 |
| tool-inventory-001 | True | True | False | True | False | 59 |
| tool-inventory-002 | True | True | False | True | False | 57 |
| tool-inventory-003 | True | True | False | True | False | 62 |
| tool-product-001 | True | True | False | True | False | 146 |
| tool-ticket-001 | True | True | False | True | False | 72 |
| tool-ticket-002 | True | True | False | True | False | 74 |
| tool-handoff-001 | True | True | False | True | False | 69 |
| no-context-001 | True | True | False | True | True | 50 |
| no-context-002 | True | True | False | True | True | 50 |
| unknown-001 | True | True | False | True | True | 53 |

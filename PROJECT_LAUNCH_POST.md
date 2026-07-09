# Project Launch Post

## 中文版

最近我完成了一个 AI 应用作品集项目：NexusAgent。

它模拟一个电子产品公司的客服与知识库场景，重点不是做一个简单聊天框，而是把 AI 应用真实需要的工程链路串起来：文档解析、RAG 检索、pgvector 向量查询、可追溯 Citation、结构化意图识别、业务工具调用、工单创建、评估脚本、Docker 和 CI。

技术栈包括 FastAPI、React、TypeScript、PostgreSQL、pgvector、Async SQLAlchemy、Pydantic、Docker 和 GitHub Actions。

这个项目里我重点处理了几个工程问题：

- 回答必须来自检索到的 chunk，并带 citation；
- 工具调用必须经过 Pydantic 校验；
- 错误日志要区分用户安全信息和服务端技术细节；
- 本地测试用 mock provider，公开 demo 不暴露 API key；
- 部署前准备 smoke test 和 release checklist。

GitHub: https://github.com/niexiaopeng02-hue/nexus-agent

Live Demo: pending deployment

## English Version

I recently finished a portfolio project called NexusAgent.

It simulates an AI customer support and knowledge-base assistant for an electronics company. The focus is not just a chatbot UI, but the engineering layers behind a real LLM application: document ingestion, RAG retrieval, pgvector search, traceable citations, structured intent routing, business tool calling, ticket creation, evaluation, Docker, and CI.

Tech stack: FastAPI, React, TypeScript, PostgreSQL, pgvector, Async SQLAlchemy, Pydantic, Docker, and GitHub Actions.

Key engineering points:

- Answers are grounded in retrieved chunks with citations.
- Tool inputs are validated with Pydantic schemas.
- User-facing errors are separated from technical server logs.
- MockProvider enables a stable public demo without exposing API keys.
- Smoke tests and a release checklist prepare the app for deployment.

GitHub: https://github.com/niexiaopeng02-hue/nexus-agent

Live Demo: pending deployment

# Roadmap

This roadmap is intentionally conservative. Items under Current are present in the repository; Next and Future are proposals, not commitments.

## Current

- Runnable implementations of conversation, tool-use, routing, planning, reflection, parallelization, prompt chaining, multi-agent collaboration, and memory patterns.
- RAG components for document loading, vector and BM25 retrieval, hybrid ranking, reranking, and context management.
- FastAPI Web/API surface, examples, Docker packaging, offline tests, and offline behavior evaluations.
- A minimal `LLMProvider` protocol while retaining the existing Gitee/OpenAI-compatible client.

## Next

- Raise deterministic coverage for agent state transitions, tool errors, memory persistence, RAG ranking, and API validation.
- Gradually expand Ruff rules and remove accumulated lint debt module by module.
- Finish provider injection across RAG and all Web factories; document compatibility contracts.
- Add structured tracing hooks and stable event schemas.
- Add offline fixtures for planning decomposition and prompt-chain parsing.
- Make examples consistently non-interactive and reproducible.
- Pin or constrain high-risk dependency ranges and automate dependency review.

## Future

- MCP tool integration with explicit permissions.
- Agent evaluation reports and regression comparison.
- Human-in-the-loop checkpoints and workflow persistence.
- Additional OpenAI-compatible providers and embedding adapters.
- Observability integrations and an evidence-backed benchmark suite.

Roadmap work should be opened as real, scoped GitHub issues only when a maintainer intends to schedule it.

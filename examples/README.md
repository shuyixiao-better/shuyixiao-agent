# Example matrix

Run commands from the repository root after `python -m pip install -e .`. The offline example needs no credentials. Other examples call a configured OpenAI-compatible endpoint and require `GITEE_AI_API_KEY` in an untracked `.env` file unless noted.

## Beginner

| Example | Purpose / pattern | Requirements | Run |
| --- | --- | --- | --- |
| `00_offline_quickstart.py` | deterministic routing + tool execution | offline | `python examples/00_offline_quickstart.py` |
| `01_simple_chat.py` | basic LangGraph conversation | API key | `python examples/01_simple_chat.py` |
| `02_tool_agent.py` | ReAct-style tool loop | API key | `python examples/02_tool_agent.py` |
| `03_custom_tool.py` | define and register tools | API key | `python examples/03_custom_tool.py` |
| `04_api_client.py` | direct client usage | API key | `python examples/04_api_client.py` |
| `05_all_tools_demo.py` | built-in deterministic tools | API key for agent portions | `python examples/05_all_tools_demo.py` |

## Intermediate

| Example | Purpose / pattern | Requirements | Run |
| --- | --- | --- | --- |
| `06_ai_powered_tools_demo.py` | LLM-backed tool functions | API key; network for URL analysis | `python examples/06_ai_powered_tools_demo.py` |
| `07_rag_basic_usage.py` | ingest and query a RAG collection | API key; embedding service/model | `python examples/07_rag_basic_usage.py` |
| `08_rag_file_upload.py` | document loading and chunking | API key; sample files | `python examples/08_rag_file_upload.py` |
| `09_rag_streaming.py` | streamed RAG response | API key | `python examples/09_rag_streaming.py` |
| `11_prompt_chaining_simple.py` | small prompt chains | API key | `python examples/11_prompt_chaining_simple.py` |
| `12_routing_agent_demo.py` | rule, keyword, LLM, hybrid routing | API key for LLM routes | `python examples/12_routing_agent_demo.py` |
| `travel_agent/travel_agent_demo.py` | tools composed into a travel workflow | API key | `python examples/travel_agent/travel_agent_demo.py` |

## Advanced

| Example | Purpose / pattern | Requirements | Run |
| --- | --- | --- | --- |
| `10_prompt_chaining_demo.py` | multi-stage reusable workflows | API key | `python examples/10_prompt_chaining_demo.py` |
| `13_parallelization_agent_demo.py` | parallel execution and aggregation | API key | `python examples/13_parallelization_agent_demo.py` |
| `14_reflection_agent_demo.py` | iterative critique and improvement | API key | `python examples/14_reflection_agent_demo.py` |
| `15_tool_use_agent_demo.py` | planned tool selection and history | API key | `python examples/15_tool_use_agent_demo.py` |
| `16_planning_agent_demo.py` | decomposition and dependency execution | API key | `python examples/16_planning_agent_demo.py` |
| `17_multi_agent_collaboration_demo.py` | role-based collaboration | API key; multiple model calls | `python examples/17_multi_agent_collaboration_demo.py` |
| `18_memory_agent_demo.py` | memory storage, retrieval, persistence | API key for memory chat | `python examples/18_memory_agent_demo.py` |

Each example's expected behavior is visible in its console output. Model-backed output is nondeterministic and is not used as an offline CI assertion. Deterministic regression checks live in [`../evals/`](../evals/) and [`../tests/`](../tests/).

"""Offline evaluation cases run by pytest and CI."""

from langchain_core.documents import Document

from evals.runner import EvalCase, evaluate
from shuyixiao_agent.agents.routing_agent import RouteConfig, RoutingAgent, RoutingStrategy
from shuyixiao_agent.rag.retrievers import KeywordRetriever


def _route(text: str) -> str:
    agent = RoutingAgent(strategy=RoutingStrategy.KEYWORD, verbose=False)
    agent.register_route(RouteConfig("code", "Code", lambda *_: "code", ["python", "代码"]))
    agent.register_route(RouteConfig("writing", "Writing", lambda *_: "writing", ["文章", "write"]))
    return agent.route(text).route_name


def _retrieve(query: str) -> str:
    documents = [Document(page_content="Python agent routing"), Document(page_content="Garden notes")]
    result = KeywordRetriever(documents, use_jieba=False).retrieve(query, top_k=1)
    return result[0][0].page_content


def test_offline_behavior_evaluations() -> None:
    cases = [
        EvalCase("route-code", "write python code", "code", _route),
        EvalCase("retrieve-agent", "agent routing", "Python agent routing", _retrieve),
    ]
    results = evaluate(cases)
    assert all(result.passed for result in results), results

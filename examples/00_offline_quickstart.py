"""Purpose: run a first agent-pattern example without an API key.

Pattern: deterministic routing plus direct tool execution.
Requirements: install the project; no network or model credentials.
Run: python examples/00_offline_quickstart.py
Expected result: the request is routed to the calculator and prints 42.0.
"""

from shuyixiao_agent.agents.routing_agent import RouteConfig, RoutingAgent, RoutingStrategy
from shuyixiao_agent.tools.basic_tools import calculate


def calculate_handler(_: str, context: dict) -> float:
    return calculate(context["expression"])


def main() -> None:
    agent = RoutingAgent(strategy=RoutingStrategy.KEYWORD, verbose=False)
    agent.register_route(
        RouteConfig(
            name="calculator",
            description="Evaluate an arithmetic expression",
            handler=calculate_handler,
            keywords=["calculate", "计算"],
        )
    )
    result = agent.route("calculate this expression", {"expression": "6 * 7"})
    if not result.success or result.handler_output != 42.0:
        raise RuntimeError(f"offline quick start failed: {result}")
    print(f"route={result.route_name} result={result.handler_output}")


if __name__ == "__main__":
    main()

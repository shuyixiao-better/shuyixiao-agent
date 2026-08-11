from shuyixiao_agent.agents.routing_agent import RouteConfig, RoutingAgent, RoutingStrategy


def test_rule_routing_prefers_higher_priority_match() -> None:
    agent = RoutingAgent(strategy=RoutingStrategy.RULE_BASED, verbose=False)
    agent.register_route(RouteConfig("general", "General", lambda *_: "general", pattern=r"python", priority=1))
    agent.register_route(RouteConfig("specific", "Specific", lambda *_: "specific", pattern=r"python", priority=5))
    result = agent.route("python help")
    assert result.success
    assert result.route_name == "specific"
    assert result.handler_output == "specific"


def test_missing_route_is_an_explicit_failure() -> None:
    result = RoutingAgent(strategy=RoutingStrategy.KEYWORD, verbose=False).route("unknown")
    assert not result.success
    assert result.route_name == "none"

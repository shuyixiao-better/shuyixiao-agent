from shuyixiao_agent.config import Settings


def test_secure_transport_is_the_default() -> None:
    assert Settings(_env_file=None).ssl_verify is True


def test_environment_values_are_parsed(monkeypatch) -> None:
    monkeypatch.setenv("AGENT_MAX_ITERATIONS", "7")
    monkeypatch.setenv("ENABLE_QUERY_REWRITE", "false")
    configured = Settings(_env_file=None)
    assert configured.agent_max_iterations == 7
    assert configured.enable_query_rewrite is False

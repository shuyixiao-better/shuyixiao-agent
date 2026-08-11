import pytest

from shuyixiao_agent.tools.basic_tools import calculate


def test_calculate_supports_documented_arithmetic() -> None:
    assert calculate("2 + 3 * (4 - 1)") == 11.0
    assert calculate("-8 / 2") == -4.0


@pytest.mark.parametrize("expression", ["2 ** 8", "abs(-1)", "1 // 2", "[1][0]"])
def test_calculate_rejects_operations_outside_its_contract(expression: str) -> None:
    with pytest.raises(ValueError):
        calculate(expression)


def test_calculate_rejects_unbounded_input() -> None:
    with pytest.raises(ValueError, match="过长"):
        calculate("1+" * 101 + "1")

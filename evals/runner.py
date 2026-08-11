"""A deliberately small, provider-independent evaluation runner."""

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class EvalCase:
    """One reproducible input and its expected behavior."""

    name: str
    input: Any
    expected: Any
    run: Callable[[Any], Any]
    check: Callable[[Any, Any], bool] = lambda actual, expected: actual == expected


@dataclass(frozen=True)
class EvalResult:
    name: str
    expected: Any
    actual: Any
    passed: bool
    error: str | None = None


def evaluate(cases: list[EvalCase]) -> list[EvalResult]:
    """Execute all cases and record failures instead of stopping early."""

    results = []
    for case in cases:
        try:
            actual = case.run(case.input)
            results.append(EvalResult(case.name, case.expected, actual, case.check(actual, case.expected)))
        except Exception as exc:  # evaluation output must retain the case-level error
            results.append(EvalResult(case.name, case.expected, None, False, str(exc)))
    return results

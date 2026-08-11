from evals.runner import EvalCase, evaluate


def test_runner_records_pass_fail_and_errors() -> None:
    cases = [
        EvalCase("pass", 2, 4, lambda value: value * 2),
        EvalCase("fail", 2, 5, lambda value: value * 2),
        EvalCase("error", None, None, lambda _: 1 / 0),
    ]
    results = evaluate(cases)
    assert [result.passed for result in results] == [True, False, False]
    assert "division by zero" in results[2].error

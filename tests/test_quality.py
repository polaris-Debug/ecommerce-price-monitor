from src.quality.run_quality import evaluate


def test_expectation_greater_than_zero():
    assert evaluate(1, "value > 0")


def test_expectation_equals_zero():
    assert evaluate(0, "value = 0")

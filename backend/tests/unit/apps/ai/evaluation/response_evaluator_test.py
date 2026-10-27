"""Tests for response keyword coverage."""

import pytest

from apps.ai.evaluation.datasets.schema import AgentOutput, EvalCase, EvalCategory
from apps.ai.evaluation.evaluators.response_evaluator import ResponseEvaluator


def evaluate_response(response, keywords):
    case = EvalCase(
        id="response-001",
        query="Tell me about OWASP",
        category=EvalCategory.PROJECT,
        expected_intent="project",
        expected_keywords=keywords,
    )
    output = AgentOutput(query=case.query, response=response, intent="project")
    return ResponseEvaluator().evaluate(case, output)


def test_all_keywords_match_case_insensitively():
    result = evaluate_response("OWASP Summer of Code", ["owasp", "summer of code"])

    assert result.passed is True
    assert result.score == 1.0
    assert result.details == {"matched_keywords": ["owasp", "summer of code"], "missing_keywords": []}


@pytest.mark.parametrize("response", ["", " \n "])
def test_empty_response_fails_without_keyword_requirements(response):
    result = evaluate_response(response, [])

    assert result.passed is False
    assert result.score == 0.0
    assert result.reason == "Response is empty"


def test_missing_keywords_reduce_score():
    result = evaluate_response("OWASP projects", ["OWASP", "flagship"])

    assert result.passed is False
    assert result.score == 0.5
    assert result.details == {"matched_keywords": ["OWASP"], "missing_keywords": ["flagship"]}
    assert result.reason == "Missing expected keywords: ['flagship']"


def test_no_keywords_match():
    result = evaluate_response("No relevant information", ["OWASP", "flagship"])

    assert result.passed is False
    assert result.score == 0.0
    assert result.details == {
        "matched_keywords": [],
        "missing_keywords": ["OWASP", "flagship"],
    }


def test_nonempty_response_passes_without_keyword_requirements():
    result = evaluate_response("An answer", [])

    assert result.passed is True
    assert result.score == 1.0


def test_partial_score_is_rounded():
    result = evaluate_response("OWASP", ["OWASP", "flagship", "projects"])

    assert result.passed is False
    assert result.score == 0.33
    assert result.details == {
        "matched_keywords": ["OWASP"],
        "missing_keywords": ["flagship", "projects"],
    }

"""Unit tests for request validation (Rules 1-4)."""
import pytest

from backend.utils.request_validator import validate_solve_payload


def test_valid_payload_returns_none(valid_solve_payload):
    """Valid payload passes all rules and returns None."""
    assert validate_solve_payload(valid_solve_payload) is None


def test_rule1_missing_equation1(valid_solve_payload):
    """Rule 1: missing equation1 returns VALIDATION_ERROR."""
    p = dict(valid_solve_payload)
    del p["equation1"]
    err = validate_solve_payload(p)
    assert err is not None
    assert err["code"] == "VALIDATION_ERROR"
    assert "equation1" in err["message"].lower()


def test_rule1_missing_equation2(valid_solve_payload):
    """Rule 1: missing equation2 returns VALIDATION_ERROR."""
    p = dict(valid_solve_payload)
    del p["equation2"]
    err = validate_solve_payload(p)
    assert err is not None
    assert err["code"] == "VALIDATION_ERROR"
    assert "equation2" in err["message"].lower()


def test_rule2_missing_variables(valid_solve_payload):
    """Rule 2: missing variables returns VALIDATION_ERROR."""
    p = dict(valid_solve_payload)
    del p["variables"]
    err = validate_solve_payload(p)
    assert err is not None
    assert err["code"] == "VALIDATION_ERROR"
    assert "variables" in err["message"].lower()


def test_rule2_variables_not_two_elements(valid_solve_payload):
    """Rule 2: variables length != 2 returns VALIDATION_ERROR."""
    p = dict(valid_solve_payload)
    p["variables"] = ["x"]
    err = validate_solve_payload(p)
    assert err is not None
    assert err["code"] == "VALIDATION_ERROR"


def test_rule2_duplicate_variable_names(valid_solve_payload):
    """Rule 2: duplicate variable names returns VALIDATION_ERROR."""
    p = dict(valid_solve_payload)
    p["variables"] = ["x", "x"]
    err = validate_solve_payload(p)
    assert err is not None
    assert err["code"] == "VALIDATION_ERROR"
    assert "duplicate" in err["message"].lower() or "Duplicate" in err["message"]


def test_rule2_empty_variable(valid_solve_payload):
    """Rule 2: empty string variable returns VALIDATION_ERROR."""
    p = dict(valid_solve_payload)
    p["variables"] = ["x", ""]
    err = validate_solve_payload(p)
    assert err is not None
    assert err["code"] == "VALIDATION_ERROR"


def test_rule3_missing_terms(valid_solve_payload):
    """Rule 3: equation without terms (and no term1/term2) returns VALIDATION_ERROR."""
    p = dict(valid_solve_payload)
    p["equation1"] = {"constant": valid_solve_payload["equation1"]["constant"]}
    err = validate_solve_payload(p)
    assert err is not None
    assert err["code"] == "VALIDATION_ERROR"


def test_rule3_legacy_term1_term2_accepted(valid_solve_payload):
    """Rule 3: legacy term1/term2 + constant is accepted."""
    p = dict(valid_solve_payload)
    eq1 = valid_solve_payload["equation1"]
    p["equation1"] = {
        "term1": eq1["terms"][0],
        "term2": eq1["terms"][1],
        "constant": eq1["constant"],
    }
    assert validate_solve_payload(p) is None


def test_non_dict_payload():
    """Non-dict payload returns error."""
    err = validate_solve_payload([])
    assert err is not None
    assert err["code"] == "VALIDATION_ERROR"

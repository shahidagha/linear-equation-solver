"""Integration tests for API endpoints (validation 422, optional solve flow)."""
import pytest
from fastapi.testclient import TestClient

from backend.api_main import app


@pytest.fixture(scope="module")
def client():
    """Test client; use default DB (may be in-memory if DATABASE_URL set in env)."""
    return TestClient(app)


def test_validation_error_missing_equation2_returns_422(client):
    """POST /v1/solve-system with missing equation2 returns 422 (Pydantic or our validator)."""
    payload = {
        "variables": ["x", "y"],
        "equation1": {
            "terms": [
                {"sign": 1, "numCoeff": 2, "numRad": 1, "denCoeff": 1, "denRad": 1},
                {"sign": 1, "numCoeff": 1, "numRad": 1, "denCoeff": 1, "denRad": 1},
            ],
            "constant": {"sign": 1, "numCoeff": 7, "numRad": 1, "denCoeff": 1, "denRad": 1},
        },
    }
    response = client.post("/v1/solve-system", json=payload)
    assert response.status_code == 422
    data = response.json()
    # Pydantic returns detail array; our validator returns code + message
    assert data.get("code") == "VALIDATION_ERROR" or "detail" in data
    if data.get("code") == "VALIDATION_ERROR":
        assert "equation2" in data.get("message", "").lower()
    else:
        assert any("equation2" in str(d) for d in data.get("detail", []))


def test_validation_error_duplicate_variables_returns_422(client):
    """POST /v1/solve-system with duplicate variable names returns 422."""
    payload = {
        "variables": ["x", "x"],
        "equation1": {
            "terms": [
                {"sign": 1, "numCoeff": 2, "numRad": 1, "denCoeff": 1, "denRad": 1},
                {"sign": 1, "numCoeff": 1, "numRad": 1, "denCoeff": 1, "denRad": 1},
            ],
            "constant": {"sign": 1, "numCoeff": 7, "numRad": 1, "denCoeff": 1, "denRad": 1},
        },
        "equation2": {
            "terms": [
                {"sign": 1, "numCoeff": 4, "numRad": 1, "denCoeff": 1, "denRad": 1},
                {"sign": -1, "numCoeff": 7, "numRad": 1, "denCoeff": 1, "denRad": 1},
            ],
            "constant": {"sign": 1, "numCoeff": 41, "numRad": 1, "denCoeff": 1, "denRad": 1},
        },
    }
    response = client.post("/v1/solve-system", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data.get("code") == "VALIDATION_ERROR"


def test_save_system_validation_error_returns_422(client):
    """POST /v1/save-system with invalid payload returns 422."""
    payload = {"variables": ["a"], "equation1": {}, "equation2": {}}
    response = client.post("/v1/save-system", json=payload)
    assert response.status_code == 422

"""Integration tests for FastAPI REST endpoints."""

import pytest
from fastapi.testclient import TestClient
from server.app import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_presets_endpoint():
    response = client.get("/api/presets")
    assert response.status_code == 200
    presets = response.json()
    assert len(presets) >= 8
    # Verify 1024-bit preset exists
    has_1024 = any(p["id"] == "prime-1024" for p in presets)
    assert has_1024
    # Verify Carmichael preset exists
    has_carmichael = any("carmichael" in p["id"] for p in presets)
    assert has_carmichael


def test_check_prime_endpoint_small_prime():
    response = client.post(
        "/api/check-prime",
        json={"number": "97", "iterations": 40},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "Prime"
    assert data["is_prime"] is True
    assert data["bitLength"] == 7
    assert data["executionTimeMs"] >= 0.0


def test_check_prime_endpoint_carmichael_number():
    response = client.post(
        "/api/check-prime",
        json={"number": "561", "iterations": 40},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "Composite"
    assert data["is_prime"] is False
    assert data["witness"] is not None


def test_check_prime_endpoint_1024_bit():
    p1024_str = (
        "179769313486231590770839156793787453197860296048756011706444423684197180216158519368947833795864925541502180565485980503646440548199239100050792877003355816639229553136239076508735759914822574862575007425302077447712589550957937778424442426617334727629299387668709205606050270810842907692932019128194467627007"
    )
    response = client.post(
        "/api/check-prime",
        json={"number": p1024_str, "iterations": 40},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "Prime"
    assert data["is_prime"] is True
    assert data["bitLength"] == 1024
    assert data["roundsCompleted"] == 40
    assert "99.99" in data["confidence"]


def test_check_prime_invalid_input():
    response = client.post(
        "/api/check-prime",
        json={"number": "not-a-number", "iterations": 40},
    )
    assert response.status_code == 422


def test_generate_prime_endpoint():
    response = client.get("/api/generate-prime?bits=128&iterations=20")
    assert response.status_code == 200
    data = response.json()
    assert data["bitLength"] == 128
    assert data["candidatesTested"] >= 1
    assert data["validationResult"]["result"] == "Prime"


def test_benchmark_endpoint():
    response = client.get("/api/benchmark?iterations=20")
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) >= 8
    assert "complexity_analysis" in data
    # Check 1024-bit entry exists in benchmark
    has_1024 = any(r["bit_length"] == 1024 for r in data["results"])
    assert has_1024

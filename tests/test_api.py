"""Smoke tests for the FastAPI app."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from aletheia.api.server import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestMetaEndpoints:
    def test_health(self, client: TestClient) -> None:
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["version"] == "0.2.0"
        assert "wisdom_graph" in data

    def test_constitution(self, client: TestClient) -> None:
        r = client.get("/constitution")
        assert r.status_code == 200
        text = r.json()["text"]
        assert "Aletheia Safety Constitution" in text
        assert "The better Aletheia works" in text


class TestWisdomEndpoints:
    def test_stats(self, client: TestClient) -> None:
        r = client.get("/wisdom/stats")
        assert r.status_code == 200
        data = r.json()
        assert data["traditions"] >= 8
        assert data["concepts"] >= 12
        assert data["claims"] >= 15

    def test_concepts(self, client: TestClient) -> None:
        r = client.get("/wisdom/concepts")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert len(r.json()) >= 12

    def test_claims(self, client: TestClient) -> None:
        r = client.get("/wisdom/claims")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert len(r.json()) >= 15

    def test_search(self, client: TestClient) -> None:
        r = client.get("/wisdom/search", params={"q": "fear of dying"})
        assert r.status_code == 200
        assert isinstance(r.json(), list)


class TestDecompose:
    def test_decompose(self, client: TestClient) -> None:
        r = client.post("/decompose", json={"statement": "I need to leave my job because everyone wants me to fail."})
        assert r.status_code == 200
        data = r.json()
        assert data["user_statement"].startswith("I need to leave")
        assert isinstance(data["layers"], list)
        assert len(data["layers"]) >= 1


class TestSocratic:
    def test_socratic(self, client: TestClient) -> None:
        r = client.post("/socratic", json={"statement": "I'm thinking about leaving my career."})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data["questions"], list)
        assert len(data["questions"]) >= 1


class TestReflect:
    def test_reflect(self, client: TestClient) -> None:
        r = client.post(
            "/reflect",
            json={
                "user_id": "test-user",
                "statement": "I'm afraid I made the wrong choice and it's too late.",
                "conversation_history": [],
                "max_questions": 2,
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert "surface_text" in data
        assert "epistemic_status" in data
        assert "reflection" in data
        assert data["reflection"]["decomposition"] is not None
        assert len(data["reflection"]["layers_invoked"]) >= 1

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.mark.skip(reason="Requires configured OpenAI/Qdrant/Superhero dependencies")
def test_ask_endpoint():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/ask",
            json={"question": "What is a Kubernetes Pod?"},
        )
        assert response.status_code == 200
        body = response.json()
        assert "answer" in body
        assert "sources" in body


import sys
from pathlib import Path
from unittest.mock import Mock

# Käytetään nimenomaan Week 5 -kansion app.py-tiedostoa.
APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

import app

app.app.template_folder = str(APP_DIR / "templates")


class FakeCursor:
    def __init__(self):
        self.saved_messages = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, query, params=None):
        if query.startswith("INSERT"):
            role = "user" if "'user'" in query else "assistant"
            self.saved_messages.append(
                {"role": role, "content": params[1]}
            )

    def fetchall(self):
        return [
            {"role": "user", "content": "Hello!"}
        ]


class FakeConnection:
    def __init__(self):
        self.fake_cursor = FakeCursor()

    def cursor(self):
        return self.fake_cursor

    def close(self):
        pass


def setup_client():
    app.app.config["TESTING"] = True
    return app.app.test_client()


def test_home_page():
    client = setup_client()
    response = client.get("/")

    assert response.status_code == 200
    assert b"Local AI Chat" in response.data


def test_health():
    client = setup_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_empty_message_is_rejected():
    client = setup_client()
    response = client.post("/api/chat", json={"message": ""})

    assert response.status_code == 400


def test_chat_with_mock_database_and_llm(monkeypatch):
    monkeypatch.setenv("OLLAMA_URL", "http://localhost:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")

    client = setup_client()
    connection = FakeConnection()

    monkeypatch.setattr(
        app, "get_db", lambda: connection
    )

    fake_response = Mock()
    fake_response.json.return_value = {
        "message": {"content": "Hello! I am a local AI."}
    }
    fake_response.raise_for_status.return_value = None

    mock_post = Mock(return_value=fake_response)
    monkeypatch.setattr(app.requests, "post", mock_post)

    response = client.post(
        "/api/chat",
        json={"message": "Hello!"},
    )

    assert response.status_code == 200
    assert response.json["reply"] == "Hello! I am a local AI."
    mock_post.assert_called_once()
    assert len(connection.fake_cursor.saved_messages) == 2


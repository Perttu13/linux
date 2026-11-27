
import os
import uuid

import pymysql
import requests
from flask import Flask, jsonify, render_template, request, session

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_PERMANENT=False,
)


def get_db():
    return pymysql.connect(
        unix_socket=os.environ["DB_SOCKET"],
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def get_session_id():
    if "chat_id" not in session:
        session["chat_id"] = str(uuid.uuid4())
    return session["chat_id"]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "commit": os.environ.get("GIT_SHA", "development"),
        }
    )


@app.route("/api/messages")
def messages():
    chat_id = get_session_id()
    connection = get_db()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT role, content, created_at FROM messages "
                "WHERE session_id = %s ORDER BY id",
                (chat_id,),
            )
            rows = cursor.fetchall()

            for row in rows:
                row["created_at"] = row["created_at"].isoformat()

            return jsonify(rows)
    finally:
        connection.close()


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message or len(message) > 4000:
        return jsonify(
            {"error": "Message must contain 1–4000 characters."}
        ), 400

    chat_id = get_session_id()
    connection = get_db()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO messages (session_id, role, content) "
                "VALUES (%s, 'user', %s)",
                (chat_id, message),
            )

            cursor.execute(
                "SELECT role, content FROM messages "
                "WHERE session_id = %s ORDER BY id DESC LIMIT 20",
                (chat_id,),
            )
            history = list(reversed(cursor.fetchall()))

        response = requests.post(
            os.environ["OLLAMA_URL"] + "/api/chat",
            json={
                "model": os.environ["OLLAMA_MODEL"],
                "messages": history,
                "stream": False,
            },
            timeout=180,
        )
        response.raise_for_status()
        answer = response.json()["message"]["content"]

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO messages (session_id, role, content) "
                "VALUES (%s, 'assistant', %s)",
                (chat_id, answer),
            )

        return jsonify({"reply": answer})

    except requests.RequestException:
        app.logger.exception("Ollama request failed")
        return jsonify(
            {"error": "The local language model is unavailable."}
        ), 503
    finally:
        connection.close()


@app.route("/api/new", methods=["POST"])
def new_chat():
    session.pop("chat_id", None)
    return jsonify({"status": "new chat started"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002)

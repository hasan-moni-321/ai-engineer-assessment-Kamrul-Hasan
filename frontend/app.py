import os
import httpx
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/ask")
def ask():
    payload = request.get_json(silent=True) or {}
    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/v1/ask",
            json=payload,
            timeout=45,
        )
        return jsonify(response.json()), response.status_code
    except httpx.HTTPError:
        return jsonify(
            {
                "code": "backend_unavailable",
                "message": "The backend is currently unavailable.",
            }
        ), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

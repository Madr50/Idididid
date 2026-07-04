"""
Appify Store Bot - Flask Keep-Alive Server
Completely sync - NO asyncio here.
"""

import time
from flask import Flask, jsonify

from config import FLASK_HOST, FLASK_PORT

app = Flask(__name__)

bot_status = {
    "status": "initializing",
    "started_at": time.time(),
    "last_ping": time.time(),
    "version": "1.0.0",
    "name": "Appify Store Bot",
}

@app.route("/")
def index():
    uptime = time.time() - bot_status["started_at"]
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    return jsonify({
        "name": bot_status["name"],
        "version": bot_status["version"],
        "status": bot_status["status"],
        "uptime": f"{hours}h {minutes}m {seconds}s",
        "last_ping": bot_status["last_ping"],
    })

@app.route("/health")
def health_check():
    return jsonify({
        "status": "healthy" if bot_status["status"] == "running" else "degraded",
        "timestamp": time.time(),
    }), 200

@app.route("/stats")
def stats():
    return jsonify({
        "status": "ok",
        "bot_status": bot_status["status"],
        "uptime_seconds": time.time() - bot_status["started_at"],
    })

def update_status(status: str):
    bot_status["status"] = status
    bot_status["last_ping"] = time.time()

def ping():
    bot_status["last_ping"] = time.time()

def run_flask_app():
    """Run Flask using Werkzeug directly - no asyncio involved."""
    from werkzeug.serving import make_server
    srv = make_server(FLASK_HOST, FLASK_PORT, app, threaded=True)
    srv.serve_forever()

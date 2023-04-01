from flask import Flask, request, jsonify
import sqlite3
from pyraft.raft import RaftNode
import threading
import time

app = Flask(__name__)
RAFT_PORT = 9000
RAFT_NODES = [
    "localhost:9000",
    "localhost:9001",
    "localhost:9002",
]

# Initialize Raft node
current_node = RaftNode(RAFT_PORT, RAFT_NODES, election_timeout_range=(500, 1000))
raft_thread = threading.Thread(target=current_node.start, daemon=True)
raft_thread.start()

# Wait for Raft leader to be elected
while current_node.leader is None:
    time.sleep(0.5)

def init_db():
    conn = sqlite3.connect("scores.db")
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player TEXT NOT NULL,
            score INTEGER NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()

init_db()

@app.route("/add_score", methods=["POST"])
def add_score():
    if not current_node.is_leader():
        return jsonify({"error": "Not the leader, try again later"}), 503

    data = request.get_json()
    player = data.get("player")
    score = data.get("score")

    if not player or not score:
        return jsonify({"error": "Invalid input"}), 400

    conn = sqlite3.connect("scores.db")
    c = conn.cursor()
    c.execute("INSERT INTO scores (player, score) VALUES (?, ?)", (player, score))
    conn.commit()
    conn.close()

    current_node.replicate_data()

    return jsonify({"success": "Score added"}), 201

@app.route("/top_n_scores", methods=["GET"])
def top_n_scores():
    n = int(request.args.get("n", 10))

    conn = sqlite3.connect("scores.db")
    c = conn.cursor()
    c.execute("SELECT * FROM scores ORDER BY score DESC LIMIT ?", (n,))
    scores = c.fetchall()
    conn.close()

    return jsonify(scores), 200

@app.route("/player_rankings", methods=["GET"])
def player_rankings():
    conn = sqlite3.connect("scores.db")
    c = conn.cursor()
    c.execute("SELECT * FROM scores ORDER BY score DESC")
    scores = c.fetchall()
    conn.close()

    return jsonify(scores), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Mock data simulating BigQuery response
mock_data = [
  {"id": "option1", "name": "Option 1", "votes": 25},
  {"id": "option2", "name": "Option 2", "votes": 42},
  {"id": "option3", "name": "Option 3", "votes": 15},
]

@app.route("/votes")
def get_votes():
    return jsonify(mock_data)

if __name__ == "__main__":
    app.run(debug=True)

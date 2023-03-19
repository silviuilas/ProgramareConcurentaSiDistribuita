import json
import os
import threading

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
from google.cloud import firestore
from google.cloud import pubsub_v1

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

pubsub_publisher = pubsub_v1.PublisherClient()
topic_path = pubsub_publisher.topic_path(os.environ["GOOGLE_CLOUD_PROJECT"], "vote-updates")

CLOUD_FUNCTION_URL = "https://addvote-lrjz7gfh4q-uc.a.run.app"

# Initialize Firestore client
db = firestore.Client()


@app.route('/votes', methods=['POST'])
def submit_vote():
    # Get the vote option from the request
    vote_option = request.json.get('option')

    if not vote_option:
        return jsonify({"status": "error", "message": "Invalid vote option"}), 400

    # Increment the vote count in Firestore
    poll_id = "JZsJSi2gaqUftJHPIB91"
    doc_ref = db.collection('votes').document(poll_id).collection("options").document(vote_option)
    doc = doc_ref.get()

    if not doc.exists:
        return jsonify({"status": "error", "message": "Vote option not found"}), 404

    client_ip = request.remote_addr
    ip_api_url = f'http://ip-api.com/json/{client_ip}'
    response = requests.get(ip_api_url).json()
    client_timezone = response['timezone'] if response['status'] == 'success' else 'Unknown'
    client_country = response['country'] if response['status'] == 'success' else 'Unknown'
    client_city = response['city'] if response['status'] == 'success' else 'Unknown'

    # Store the vote information in Firestore
    vote_data = {
        'ip': client_ip,
        'timezone': client_timezone,
        'country': client_country,
        'city': client_city,
    }

    data = {
        'poll_id': poll_id,  # Replace with your poll_id
        'document_id': vote_option,
        'payload': vote_data,
    }

    response = requests.post(CLOUD_FUNCTION_URL, json=data)
    if response.status_code == 200 and response.text == 'Vote saved successfully!':
        new_vote_count = len(list(doc_ref.collection("vote").stream()))

        vote_update = {"option": vote_option, "count": new_vote_count}
        pubsub_publisher.publish(topic_path, json.dumps(vote_update).encode('utf-8'))
        return jsonify({"status": "success"})
    return jsonify({'status': 'error', 'message': 'Failed to submit vote'}), 500


def fetch_data_from_firestore():
    collection = db.collection('votes').document("JZsJSi2gaqUftJHPIB91").collection("options")
    docs = collection.stream()
    data = []

    for doc in docs:
        vote_data = doc.to_dict()
        vote_data['id'] = doc.id
        vote_data['votes'] = len(list(collection.document(doc.id).collection("vote").stream()))
        data.append(vote_data)

    return data


def callback(message):
    print(f"Received message: {message}")
    socketio.emit("vote_update", message.data.decode('utf-8'))
    message.ack()


def subscribe_to_vote_updates():
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(os.environ["GOOGLE_CLOUD_PROJECT"], "vote-updates-sub")

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}...")

    with subscriber:
        try:
            streaming_pull_future.result()
        except Exception as e:
            streaming_pull_future.cancel()
            print(f"Listening for messages on {subscription_path} threw an exception: {e}")


@app.route("/votes", methods=["GET"])
def get_votes():
    vote_data = fetch_data_from_firestore()
    return jsonify(vote_data)


if __name__ == "__main__":
    listener_thread = threading.Thread(target=subscribe_to_vote_updates, daemon=True)
    listener_thread.start()
    # Remove the following line
    # app.run(debug=True)
    socketio.run(app, host="0.0.0.0", port=5001, allow_unsafe_werkzeug=True)

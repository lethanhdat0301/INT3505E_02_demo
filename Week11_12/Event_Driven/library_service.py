from flask import Flask, request, jsonify
from redis import Redis
import json
from datetime import datetime

app = Flask(__name__)
redis = Redis(host="localhost", port=6379)

EVENT_CHANNEL = "library_events"

@app.route("/borrow", methods=["POST"])
def borrow_book():
    payload = request.json

    event = {
        "eventType": "BookBorrowed",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "userId": payload["userId"],
            "bookId": payload["bookId"],
            "title": payload["title"],
            "borrowDate": payload["borrowDate"]
        }
    }

    # Publish event
    redis.publish(EVENT_CHANNEL, json.dumps(event))

    return jsonify({"message": "Borrow success", "eventPublished": event})

if __name__ == "__main__":
    app.run(port=5001)

from flask import Flask
from redis import Redis
import json
import threading

app = Flask(__name__)
redis = Redis(host="localhost", port=6379)

EVENT_CHANNEL = "library_events"

def handle_event(event):
    print("\n📩 EVENT RECEIVED:")
    print(json.dumps(event, indent=2))

    if event["eventType"] == "BookBorrowed":
        print(f"📚 Sending email: User {event['data']['userId']} borrowed '{event['data']['title']}'")

def subscribe_events():
    pubsub = redis.pubsub()
    pubsub.subscribe(EVENT_CHANNEL)

    print("🔍 Notification Service: Listening for events...")
    for message in pubsub.listen():
        if message["type"] == "message":
            event = json.loads(message["data"])
            handle_event(event)

@app.route("/")
def home():
    return "Notification Service Running"

if __name__ == "__main__":
    threading.Thread(target=subscribe_events).start()
    app.run(port=5002)

from flask import Flask, request, jsonify

app = Flask(__name__)

processed = set()

@app.route("/webhook/order", methods=["POST"])
def webhook_order():
    data = request.get_json()
    idempotency = request.headers.get("Idempotency-Key")

    print("\n Incoming Webhook")
    print("Idempotency:", idempotency)
    print("Payload:", data)


    if idempotency in processed:
        print("Duplicate event → ignored")
        return jsonify({"message": "Already processed"}), 200

    import random
    if random.random() < 0.3:
        print("Random failure!")
        return jsonify({"error": "Server busy"}), 500

    processed.add(idempotency)

    print(f"Order {data['order_id']} updated to {data['status']}")

    return jsonify({"message": "Webhook OK"}), 200


app.run(port=5000)

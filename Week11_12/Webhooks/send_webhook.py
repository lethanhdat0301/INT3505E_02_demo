import requests
import uuid
import time
import random

WEBHOOK_URL = "http://localhost:5000/webhook/order"

def send_webhook(payload):
    idempotency_key = str(uuid.uuid4())
    headers = {"Idempotency-Key": idempotency_key}

    for attempt in range(5):
        print(f"\nTry #{attempt+1} sending webhook...")

        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)

        print("Response:", response.status_code, response.text)

        if 200 <= response.status_code < 300:
            print("Delivered!")
            return
        
        if 400 <= response.status_code < 500:
            print("Permanent error → No retry.")
            return
        
        wait = 2 ** attempt
        print(f"Temporary error → retry in {wait}s")
        time.sleep(wait)

    print("Failed after retries!")


def on_order_shipped(order):
    print("Event fired: ORDER_SHIPPED")
    send_webhook(order)

order = {
    "order_id": "1",
    "status": "SHIPPED",
    "amount": 150000,
    "customer": "Vu Tung Lam"
}

on_order_shipped(order)

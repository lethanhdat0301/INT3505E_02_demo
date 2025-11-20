from fastapi import FastAPI, Request
import json, time

app = FastAPI()

def write_audit(event, user, ip):
    entry = {
        "event": event,
        "user": user,
        "ip": ip,
        "time": time.time()
    }
    with open("audit.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")

@app.post("/login")
async def login(request: Request):
    data = await request.json()
    write_audit("LOGIN_ATTEMPT", data.get("username"), request.client.host)
    return {"msg": "ok"}

from flask import Flask, request, jsonify
import logging
import time
from prometheus_client import Counter, generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis

app = Flask(__name__)


logging.basicConfig(
    filename='audit.log',
    level=logging.INFO,
    format='%(asctime)s %(message)s'
)

redis_client = Redis(host='localhost', port=6379, db=0)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["5 per minute"]
)

limiter.init_app(app)

login_counter = Counter('login_requests_total', 'Số lần gọi /login')

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.json
    username = data.get('username')
    ip = request.remote_addr

    logging.info(f"LOGIN_ATTEMPT user={username} ip={ip}")

    login_counter.inc()

    return jsonify({"msg": "ok"})


@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    app.run(debug=True)

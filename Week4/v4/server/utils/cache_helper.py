from flask import make_response, jsonify

def cache_response(data, max_age=60):
    resp = make_response(jsonify(data))
    resp.headers["Cache-Control"] = f"public, max-age={max_age}"
    resp.headers["Content-Type"] = "application/json"
    return resp

from flask import Flask, jsonify, make_response
from _common import cors_headers, issue_csrf_token, preflight_if_needed

app = Flask(__name__)

@app.route("/api/csrf", methods=["GET", "OPTIONS"])
def get_csrf():
    pf = preflight_if_needed()
    if pf: 
        return pf
    resp = make_response(jsonify({"ok": True}))
    token, resp = issue_csrf_token(resp)
    resp.headers["X-CSRF-Token"] = token
    return cors_headers(resp)

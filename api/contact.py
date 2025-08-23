import os, requests
from flask import Flask, request, jsonify, make_response
from _common import cors_headers, preflight_if_needed, check_origin_and_referer, limiter, verify_csrf, sanitize

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
CONTACT_TO = os.getenv("CONTACT_TO", "")
FROM_EMAIL = "info@kvold.biz"
SUBJECT = "New kVold.biz inquiry"
RESEND_URL = "https://api.resend.com/emails"

app = Flask(__name__)

@app.route("/api/contact", methods=["POST", "OPTIONS"])
def contact():
    pf = preflight_if_needed()
    if pf: 
        return pf

    if not check_origin_and_referer():
        return cors_headers(make_response(jsonify({"ok": False, "error": "Forbidden (origin)"}), 403))
    if not verify_csrf():
        return cors_headers(make_response(jsonify({"ok": False, "error": "Bad CSRF"}), 403))
    if not limiter(max_per_min=8):
        return cors_headers(make_response(jsonify({"ok": False, "error": "Rate limited"}), 429))

    data = request.get_json(silent=True) or {}
    first_name = sanitize(data.get("firstName", ""))
    job_title  = sanitize(data.get("jobTitle", ""))
    email      = sanitize(data.get("email", ""))
    business   = sanitize(data.get("business", ""))
    problem    = sanitize(data.get("problem", ""))
    additional = sanitize(data.get("additional", ""))

    html = f"""
    <div style='font-family:Arial,sans-serif;font-size:14px;color:#0f172a'>
      <h2>New Inquiry from kVold.biz</h2>
      <table cellpadding='6' cellspacing='0' style='border-collapse:collapse'>
        <tr><td><strong>First Name</strong></td><td>{first_name}</td></tr>
        <tr><td><strong>Job Title</strong></td><td>{job_title}</td></tr>
        <tr><td><strong>Email</strong></td><td>{email}</td></tr>
        <tr><td><strong>Business Description</strong></td><td>{business}</td></tr>
        <tr><td><strong>Problem Statement</strong></td><td>{problem}</td></tr>
        <tr><td><strong>Additional Information</strong></td><td>{additional}</td></tr>
      </table>
    </div>
    """.strip()

    if not (RESEND_API_KEY and CONTACT_TO):
        return cors_headers(make_response(jsonify({"ok": False, "error": "Server not configured"}), 500))

    payload = {
        "from": FROM_EMAIL,
        "to": [CONTACT_TO],
        "subject": SUBJECT,
        "html": html,
        "reply_to": email or FROM_EMAIL
    }

    try:
        r = requests.post(
            RESEND_URL,
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=10
        )
        ok = r.status_code in (200, 202)
        if not ok:
            return cors_headers(make_response(jsonify({"ok": False, "error": f"Resend status {r.status_code}", "body": r.text}), 502))
    except requests.RequestException as e:
        return cors_headers(make_response(jsonify({"ok": False, "error": str(e)}), 502))

    return cors_headers(make_response(jsonify({"ok": True})))

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"ok": True})

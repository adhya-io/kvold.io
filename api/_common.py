import os, time
from flask import request, make_response
from itsdangerous import URLSafeSerializer, BadSignature

ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "")
SITE_HOST = os.getenv("SITE_HOST", "")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")

_RATE = {}

def cors_headers(resp):
    origin = request.headers.get("Origin", "")
    allowed = ALLOWED_ORIGIN or origin  # if unset, allow same-origin deployment
    if origin and allowed and origin == allowed:
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Vary"] = "Origin"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, X-CSRF-Token"
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    return resp

def preflight_if_needed():
    if request.method == "OPTIONS":
        return cors_headers(make_response(("", 204)))

def check_origin_and_referer():
    origin = request.headers.get("Origin", "")
    referer = request.headers.get("Referer", "")
    # If env isn't set, accept same-origin (Origin must equal Host)
    host = request.headers.get("Host", "")
    fallback_ok = (not ALLOWED_ORIGIN) and origin and (origin.replace("https://","").replace("http://","").startswith(host))
    origin_ok = (not ALLOWED_ORIGIN) or (origin == ALLOWED_ORIGIN) or fallback_ok
    referer_ok = (not SITE_HOST) or (SITE_HOST in referer)
    return origin_ok and referer_ok

def limiter(max_per_min=10):
    ip = request.headers.get("x-forwarded-for", request.remote_addr or "unknown").split(",")[0].strip()
    now = time.time()
    window = 60
    _RATE.setdefault(ip, [])
    _RATE[ip] = [t for t in _RATE[ip] if now - t < window]
    if len(_RATE[ip]) >= max_per_min:
        return False
    _RATE[ip].append(now)
    return True

def get_serializer():
    return URLSafeSerializer(SECRET_KEY, salt="kvold.csrf")

def issue_csrf_token(resp):
    s = get_serializer()
    token = s.dumps({"ts": int(time.time())})
    resp.set_cookie("csrf", token, httponly=True, secure=True, samesite="Strict", max_age=3600)
    return token, resp

def verify_csrf():
    s = get_serializer()
    header = request.headers.get("X-CSRF-Token", "")
    cookie = request.cookies.get("csrf", "")
    try:
        h = s.loads(header)
        c = s.loads(cookie)
    except BadSignature:
        return False
    return h == c

def sanitize(s: str) -> str:
    return (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

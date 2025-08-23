# kVold Full‑Stack (Vercel) — Frontend + Python/Flask API

Single repository you can deploy to Vercel:
- Static frontend (index.html + assets/)
- Python/Flask serverless functions under /api

## Endpoints
- `GET /api/csrf` — issues a CSRF cookie and returns the token in `X-CSRF-Token`
- `POST /api/contact` — accepts JSON and sends email via Resend

## Environment Variables (Vercel → Settings → Environment Variables)
- `ALLOWED_ORIGIN` — e.g., `https://kvold.biz` (optional; if omitted, same‑origin allowed)
- `SITE_HOST` — e.g., `kvold.biz` (optional; referer check)
- `SECRET_KEY` — random string for CSRF signing
- `RESEND_API_KEY` — your Resend API key (`re_xxxxxx`)
- `CONTACT_TO` — destination inbox address

## Frontend
- Already wired to call `/api/csrf` then `/api/contact` with the required fields:
  - firstName, jobTitle, email, business, problem, additional

## Local Development
1. Serve the static frontend (any static server) if you want, but for simplicity just deploy to Vercel.
2. For local API testing:
   ```bash
   pip install -r requirements.txt
   export ALLOWED_ORIGIN=http://localhost:5173
   export SITE_HOST=localhost:5173
   export SECRET_KEY=dev-secret
   export RESEND_API_KEY=re_xxxxxx
   export CONTACT_TO=you@example.com
   flask --app api/contact.py run -p 3000
   ```
3. Ensure the frontend fetches `http://localhost:3000/api/...` during local testing, or run both behind the same origin via a local proxy.

## Deploy to Vercel
- Push this folder to GitHub/GitLab and import the repo into Vercel, or run `vercel` from this directory.
- Add env vars for Production (and Preview if needed).
- Vercel will host static files and route `/api/*` to the Python functions.

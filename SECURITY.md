# JARVIS AT SCALE — Security Documentation & Hardening

---

## 1. Authentication & Authorization Model
* **Password Security**: Passwords are formatted using PBKDF2-HMAC-SHA256 with a 16-byte random salt and 100,000 iterations (`salt_hex:hash_hex`). Plaintext passwords are never stored or logged.
* **Token Authentication**: Authenticated requests require an `Authorization: Bearer <token>` header verified via HMAC-SHA256 signature and expiration check.
* **Resource Ownership**: Every resource (`conversations`, `messages`, `memories`, `profiles`, `tasks`, `jobs`) enforces user ownership server-side (`current_user.id == resource.user_id`). Attempting to access another user's resource returns `HTTP 403 Forbidden`.

---

## 2. Rate Limiting & Abuse Protection
Rate limits are enforced using sliding window counters:
* `POST /auth/register` & `POST /auth/login`: Maximum 10 requests per minute per IP.
* `POST /chat`: Maximum 30 requests per minute per user.
* `POST /jobs`: Maximum 3 active concurrent background jobs per user.
* `WS /ws/{session_id}`: Maximum 5 concurrent WebSocket connections per user and 60 messages per minute per connection.

---

## 3. Server-Side Request Forgery (SSRF) Protection
The `web_fetch` tool validates target URLs using `SSRFProtector.validate_url()`:
* **Blocked IP Ranges**: Loopback (`127.0.0.0/8`, `::1`), Private Class A/B/C (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), Link-Local (`169.254.0.0/16`), Cloud Metadata (`169.254.169.254`).
* **Blocked Hostnames**: `localhost`, `metadata.google.internal`.
* **Redirect Validation**: Re-validates the final URL after HTTP redirects to prevent open-redirect SSRF bypasses.

---

## 4. Multimodal & File Upload Safeguards
* **File Extensions**: Only `.png`, `.jpg`, `.jpeg`, `.webp`, `.txt`, `.md` are allowed.
* **File Size Limit**: Hard size limit of 10 MB per file. Requests exceeding 10 MB return `HTTP 413 Payload Too Large`.
* **Prompt Injection Isolation**: External web fetch and document content are wrapped inside explicit untrusted boundary notes (`--- START UNTRUSTED DATA ---`) to prevent prompt override attacks.

---

## 5. Tool Safety Categories
* **`low_risk`**: `calculator`, `web_search`
* **`network_access`**: `web_fetch` (SSRF protected)
* **`restricted`**: Destructive shell execution or system modification tools require explicit user authorization.

---

## 6. HTTP Security Headers
Applied by `SecurityHeadersMiddleware`:
* `X-Content-Type-Options: nosniff`
* `X-Frame-Options: DENY`
* `X-XSS-Protection: 1; mode=block`
* `Referrer-Policy: strict-origin-when-cross-origin`

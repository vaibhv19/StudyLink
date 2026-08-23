# StudyLink Security Architecture & Policy

## Executive Summary

StudyLink is an academic resource-sharing, marketplace, and RAG-powered platform. Security is built into the architecture following the defense-in-depth paradigm, enforcing strict token-based authentication, object-level authorization, database isolation, parameter sanitization, and cloud infrastructure hardening.

---

## 1. Authentication & Session Management

- **Authentication Framework**: Django REST Framework with `djangorestframework-simplejwt`.
- **JWT Token Lifecycle**:
  - **Access Tokens**: Short-lived (15–60 minutes) HMAC-SHA256 signed JSON Web Tokens.
  - **Refresh Tokens**: Long-lived (7–14 days) sliding expiration tokens stored securely on the client.
  - **Token Blacklisting**: Enabled via `rest_framework_simplejwt.token_blacklist` upon logout or credential change.
- **Identity Isolation**: Supabase Auth and third-party OAuth are omitted in v1 to enforce a single authoritative authentication provider managed exclusively by Django ORM.

---

## 2. Authorization & Access Control (RBAC)

- **Permission Classes**: DRF `IsAuthenticated` and custom object-level permissions (`IsOwnerOrReadOnly`).
- **Resource Ownership Enforcement**:
  - **Vault Documents & Chunks**: Read/Query access restricted to authenticated academic domain users.
  - **Market Listings**: Write/Update operations restricted to item owners.
  - **Market Requests**: Status transitions (`PENDING` -> `ACCEPTED` / `REJECTED`) strictly enforced via database pessimistic locking (`SELECT FOR UPDATE`) to prevent unauthorized or race-condition state mutations.
- **Admin & API Scope**: Administrative endpoints protected by Django `is_staff` / `is_superuser` flags.

---

## 3. Data Protection & Encryption

- **Data in Transit**: Mandatory TLS 1.3 / HTTPS encryption specification for external traffic (Supabase PostgreSQL, S3 media storage, and future Cloud Run/Vercel endpoints).
- **Data at Rest**:
  - PostgreSQL database encrypted using AES-256 at the storage layer.
  - S3 media storage buckets enforce server-side encryption (`SSE-S3`).
- **Secret Management**: Zero secrets or API keys in source control. Environment variables injected at runtime via `.env` files locally and designed for Google Cloud Secret Manager / Cloud Run injection in production.

---

## 4. Vector Database & RAG Security Architecture

- **Single-Document Scope Boundary**: RAG queries strictly isolate chunk retrieval to the document specified by the user's active session context (`resource_id`).
- **pgvector Isolation**: Similarity searches utilize parameterized cosine distance queries (`<=>` operator) via Django ORM and raw SQL query parameters to prevent SQL injection.
- **Prompt Injection Defense**: User queries passed to Google Gemini API (`gemini-1.5-flash`) are sanitized and formatted inside strict system prompts (`backend/rag/search.py`) separating system instructions from untrusted user inputs.

---

## 5. Network & Infrastructure Security

- **Container Hardening**: Multi-stage Docker build (`backend/Dockerfile`) running non-root WSGI processes via `gunicorn`.
- **CORS Policy**: Configured via `django-cors-headers`. Restricted explicitly to authorized frontend domain origins (`CORS_ALLOWED_ORIGINS`).
- **Database Connection Security**: SSL connection mode (`sslmode=require`) enforced for remote Supabase PostgreSQL connectivity.

---

## 6. Vulnerability Disclosure Policy

If you discover a security vulnerability within StudyLink, please report it responsibly:

1. **Email**: `security@studylink.dev` or contact the repository owner directly.
2. **Details**: Include a detailed description, proof of concept, and reproduction steps.
3. **Response Time**: Acknowledgement within 24 hours and remediation update within 7 days.

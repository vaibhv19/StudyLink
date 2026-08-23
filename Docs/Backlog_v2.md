# StudyLink — v2 Deferred Scope Backlog

This document explicitly tracks features and infrastructure components deferred from **StudyLink v1** to **v2**. These items are intentionally cut from v1 to streamline setup, reduce deployment friction, and prioritize rapid delivery, but remain part of the long-term project vision.

---

## 1. Deferred Features & Rationale

### 1.1 Google OAuth & GitHub OAuth Integration
- **v1 Status:** Deferred (v1 uses JWT email/password auth only).
- **Description:** Third-party social logins via Google OAuth 2.0 and GitHub OAuth, including account-linking flows when an email collision occurs with an existing local account.
- **Why Deferred from v1:** Google OAuth Consent Screen setup, GCP domain verification, and GitHub OAuth Application callback URI management were identified as the slowest, least-automatable manual friction points in previous cloud deployments.
- **v2 Implementation Plan:**
  - Add `provider`, `linked_google`, `linked_github` columns to `users` table via non-breaking DB migration.
  - Implement `/api/v1/auth/social/google/`, `/api/v1/auth/social/github/`, and `/api/v1/auth/social/link-confirm/` API endpoints.
  - Add Google and GitHub social login buttons to React frontend.

### 1.2 Celery + Redis Asynchronous Background Processing
- **v1 Status:** Deferred (v1 processes PDF ingestion and notifications synchronously).
- **Description:** Celery worker task queues (`ingestion`, `notifications`, `default`) backed by a Redis message broker to offload CPU/IO-heavy operations.
- **Why Deferred from v1:** Setting up Redis containers, configuring Celery queues, and managing worker lifecycle monitoring were among the slowest, least-automatable deployment steps.
- **v1 Tradeoff:** Ingestion/embedding runs synchronously in the HTTP upload request cycle. Upload response time scales with PDF size, accepted as a v1 limitation.
- **v2 Implementation Plan:**
  - Deploy Redis instance on cloud/upstash or Docker worker container.
  - Wrap PDF extraction and Gemini vector embedding in Celery `@shared_task`.
  - Shift notification triggers to background worker queues.

### 1.3 Custom Domain, DNS & SSL Setup
- **v1 Status:** Deferred (v1 uses default Cloud Run `*.run.app` and Vercel `*.vercel.app` URLs).
- **Description:** Custom domain mapping (e.g. `studylink.app`), DNS CNAME/A record routing, and custom SSL certificate provisioning.
- **Why Deferred from v1:** DNS propagation delays and domain registrar configurations add unnecessary overhead to initial cloud deployment verification.
- **v2 Implementation Plan:**
  - Map custom domain in Google Cloud Run domain mappings and Vercel domain settings.
  - Configure DNS records (A/AAAA/CNAME) at domain registrar.

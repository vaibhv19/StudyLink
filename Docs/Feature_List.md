# StudyLink — Feature List

**Project name:** StudyLink
**Stack:** Django + React
**Structure:** Two modules — Resource Vault (digital) + Giveaway Marketplace (physical, OLX-style)

---

## Module 1 — Resource Vault

- Upload study material (PDFs, notes) tagged by subject/course
- Filterable search (subject, course, tags)
- Doubt board / discussion per resource
- Rating/upvote system so quality material surfaces
- **Chat with your notes** — student picks an uploaded PDF and asks questions about it; answered via a Gemini-based RAG pipeline (pgvector similarity search over that document's chunks), scoped to one document at a time — not cross-document retrieval

## Module 2 — Giveaway Marketplace (OLX-style)

- List an item to give away: title, condition, subject/course tag, description, photo, pickup_area
- Search/filter by subject, course, condition, pickup_area
- Status lifecycle: `Available → Requested → Given Away` (falls back to `Available` if a request doesn't work out)
- Request flow: interested users send a request; owner reviews pending requests and picks one; other requesters get notified the item's gone
- Owner dashboard: your listings + incoming requests, in one place
- **Local pickup only** — no shipping, no payment integration. Match people, they coordinate the handoff themselves. This is the deliberate scope boundary that keeps it from becoming an e-commerce project.

---

## Backend Layer (Django)

- Auth: JWT (access/refresh tokens) for v1 local accounts
- Data model: `Resource` (vault) and `Listing` (marketplace) as separate entities, both tied to Subject/Course tags
- File/image storage: Supabase Storage (uploaded PDFs, listing photos)
- Vector storage: Supabase Postgres with `pgvector` (resource chunk embeddings for the chat-with-notes feature, created synchronously on upload in v1)
- Notification on request status change (owner gets notified of new requests; requesters get notified when an item's taken)
- Search/filter query logic across both modules
- Core engineering: validation, pagination, permissions (only owner can manage their own listings/resources)

## Frontend Layer (React)

- Two clear sections: Vault (browse/upload notes) and Marketplace (browse/list giveaways)
- Filter UI shared across both (subject/course tags)
- Request/owner dashboard views
- Chat interface for chat-with-notes (answer + source excerpt display)

---

## Deployment Architecture & Prepared Readiness

- Database + Storage: Supabase (Postgres + Storage; active)
- Backend Containerization: Dockerized Django backend (`backend/Dockerfile`), prepared for GCP Cloud Run
- Frontend Static Assets: Vite React build (`frontend/vercel.json`), prepared for Vercel hosting
- **v1 Deployment Status:** Intentionally Deferred (❎) — maintainable and reproducible locally; live cloud deployment deferred to v2.

---

## Deferred to v2 Backlog

- **Public Cloud Hosting:** Defer active GCP Cloud Run and Vercel hosting deployment to v2 (avoiding sleeping tier cold starts and GCP account pre-payment requirements).
- **OAuth Integration:** Google OAuth + GitHub OAuth social login and account linking logic deferred to v2.
- **Async Background Processing:** Celery + Redis task queue for async ingestion and notifications deferred to v2.
- **Custom Domain:** Custom DNS / domain configuration deferred to v2.

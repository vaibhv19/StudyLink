# StudyLink — Feature List

**Project name:** StudyLink
**Stack:** Django + React
**Structure:** Two modules — Resource Vault (digital) + Giveaway Marketplace (physical, OLX-style)

---

## Module 1 — Resource Vault

- Upload study material (PDFs, notes) tagged by subject/course
- Filterable search (subject, course, tags)
- Doubt board / discussion per resource (from the original VidyaLink idea)
- Rating/upvote system so quality material surfaces
- **Chat with your notes** — student picks an uploaded PDF and asks questions about it; answered via a Gemini-based RAG pipeline (pgvector similarity search over that document's chunks), scoped to one document at a time — not cross-document retrieval

## Module 2 — Giveaway Marketplace (OLX-style)

- List an item to give away: title, condition, subject/course tag, description, photo, pickup location/area
- Search/filter by subject, course, condition, location
- Status lifecycle: `Available → Requested → Given Away` (falls back to `Available` if a request doesn't work out) — same state-machine pattern as Trajectory's application status
- Request flow: interested users send a request; owner reviews pending requests and picks one; other requesters get notified the item's gone
- Owner dashboard: your listings + incoming requests, in one place
- **Local pickup only** — no shipping, no payment integration. Match people, they coordinate the handoff themselves. This is the deliberate scope boundary that keeps it from becoming an e-commerce project.

---

## Backend Layer (Django)

- Auth: JWT (access/refresh) + Google OAuth + GitHub OAuth
- Data model: `Resource` (vault) and `Listing` (marketplace) as separate entities, both tied to Subject/Course tags
- File/image storage: Supabase Storage (uploaded PDFs, listing photos)
- Vector storage: Supabase Postgres with `pgvector` (resource chunk embeddings for the chat-with-notes feature)
- Notification on request status change (owner gets notified of new requests; requesters get notified when an item's taken)
- Search/filter query logic across both modules
- Core engineering: validation, pagination, permissions (only owner can manage their own listings/resources)

## Frontend Layer (React)

- Two clear sections: Vault (browse/upload notes) and Marketplace (browse/list giveaways)
- Filter UI shared across both (subject/course tags)
- Request/owner dashboard views
- Chat interface for chat-with-notes (answer + source excerpt display)

---

## Deployment

- Database + Storage: Supabase (Postgres + Storage; not Supabase Auth)
- Backend: Django, containerized, deployed to GCP Cloud Run
- Frontend: React, deployed to Vercel

## Open Question

- How an account created via email/JWT merges (or doesn't) with a later OAuth login using the same email address — not yet resolved.

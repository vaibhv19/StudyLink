# Phase 13 — Documentation & Project Audit

This phase covers completing the **Documentation** and performing a **Project Audit** before project handover. It outlines README templates for the monorepo root, `backend/`, and `frontend/` folders, and provides security, performance, and API compliance validation checklists.

---

## 1. Documentation Structure & Audits

### 1.1 Directory Structure
```text
StudyLink/ (Monorepo Root)
├── README.md                   # Master Repository Guide
├── backend/
│   └── README.md               # Django Developer Guide
└── frontend/
    └── README.md               # React Developer Guide
```

### 1.2 Purpose
Provides clear documentation for recruiters and developers to understand the project architecture, run it locally, and review technical decisions.

---

## 2. Implementation Tasks

### 2.1 Django Backend Layer (`backend/`)

#### Feature: Backend Developer Guides
Write documentation for backend operations.

##### Task 13.01.01: Write Django Developer Guide
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Phase 08 complete
- **Task Description:** Write `backend/README.md` covering:
  - How to set up the virtualenv and run `pip install -r requirements.txt`.
  - Database migrations, seeding data (`python manage.py seed_tags`), and starting the server.
  - Running pytest / Django unit tests.
- **Definition of Done:**
  - `backend/README.md` contains clear local setup and execution instructions.

##### Task 13.01.02: Configure API Swagger Schema
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Phase 08 complete
- **Task Description:** Install and configure `drf-spectacular` to generate interactive API documentation at `/api/v1/schema/swagger-ui/`.
- **Definition of Done:**
  - Navigating to the Swagger URL loads the API documentation.

---

### 2.2 React Frontend Layer (`frontend/`)

#### Feature: Frontend Developer Guides
Write documentation for frontend operations.

##### Task 13.02.01: Write React Developer Guide
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Phase 09 complete
- **Task Description:** Write `frontend/README.md` covering:
  - Installing dependencies with `npm install`.
  - Local configuration variables in `.env`.
  - Running the dev server with `npm run dev` and building production assets.
- **Definition of Done:**
  - `frontend/README.md` contains clear local setup and execution instructions.

---

### 2.3 Master Repositories Guide & Auditing

#### Feature: Master Repository Documentation
Write the main project documentation.

##### Task 13.03.01: Write Master Repository README
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Phase 10 complete
- **Task Description:** Write the main `README.md` in the workspace root, detailing:
  - The project's architecture, folder structure, and core technologies.
  - A summary of features (Resource Vault, RAG Chat, Marketplace).
  - Quick-start instructions for local setup and execution.
  - Project status overview (v1 complete, public deployment intentionally deferred).
- **Definition of Done:**
  - The root README is complete, confident, and provides a clear project overview.

##### Task 13.03.02: Perform Security & Performance Audit
- **Estimated Size:** S
- **Risk:** Medium
- **Prerequisites:** Phase 10 complete
- **Task Description:** Run final checks on the application codebase:
  - Verify that `settings_prod.py` configures `DEBUG = False` and security headers for deployment readiness.
  - Test the RAG similarity search threshold, ensuring weak queries are blocked.
  - Verify database pooler and Supabase pgvector configuration.
- **Definition of Done:**
  - Audit verdict: **PASS — Ready to proceed to deployment**. (Actual cloud deployment intentionally deferred after audit).

---

## 3. Pre-Flight Release Audit Checklist

Before project handover, verify that the application meets the following criteria:

```text
[ ] Security check:
    - Django settings set DEBUG = False.
    - SECURE_SSL_REDIRECT is enabled.
    - Credentials are read from env variables; no secrets are committed in the code.
    - CORS origins are restricted to allowed frontend domains.

[ ] Database check:
    - All database migrations are applied.
    - pgvector HNSW indexes are active on embedding columns.
    - Database pooler connection timeout configurations are set.

[ ] AI RAG check:
    - Gemini RAG queries are restricted to the selected document.
    - Scanned PDF images return the "UNSEARCHABLE" status.
    - Similarity cutoff is active and blocks weak queries.

[ ] Marketplace check:
    - Concurrency locks prevent double-acceptance.
    - Status histories are logged for all transitions.
    - Soft deletes work correctly.
```

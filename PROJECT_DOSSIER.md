# StudyLink

## 1. Project Overview

**StudyLink** is a full-stack academic resource and peer collaboration platform designed to address two core student workflow needs:
1. **The Resource Vault**: A digital repository for uploading course materials and PDFs, featuring an interactive Doubt Board discussion tree, upvoting, and a document-scoped **Retrieval-Augmented Generation (RAG)** assistant powered by Google Gemini and PostgreSQL `pgvector` for grounded Q&A with exact page citations.
2. **The Peer-to-Peer Marketplace**: A hyper-local giveaway exchange for physical textbooks, lab gear, and notes, enforced by a strict, ACID-compliant **Listing State Machine** with database row-level pessimistic locking (`select_for_update`) to eliminate race conditions during concurrent item requests.

The application is structured as a monorepo containing a **Django 5.1 / Django REST Framework** backend and a **React 18 / Vite / Tailwind CSS** frontend, configured for hybrid local-cloud execution with Supabase PostgreSQL/S3 and container-ready release profiles.

---

## 2. Why I Built It

University academic material exchanges frequently collapse into two chaotic extremes:
- Digital notes are scattered across unindexed chat channels, Google Drive folders, and messaging groups where finding specific conceptual answers inside a 60-page PDF requires manual scanning.
- Physical textbooks and surplus lab equipment are either abandoned at the end of a semester or posted to noisy general-purpose social classifieds where coordinating handoffs is plagued by ghosting, double-promising, and lack of state clarity.

I built StudyLink to explore how coupling strict database concurrency patterns with modern scoped vector retrieval can solve both problems in a unified campus utility. Rather than building a generic e-commerce platform or a superficial chat-with-PDF wrapper, the goal was to implement a resilient, domain-driven architecture with clean state boundaries, explicit locking mechanisms, and transparent citation attribution.

---

## 3. Problem / Question

1. **State Integrity under Concurrent Contention:** How do we prevent race conditions and double-claims when multiple students request the same physical giveaway item simultaneously, without introducing bloated e-commerce checkout flows or payment gateways?
2. **Scoped Vector Retrieval & Hallucination Mitigation:** How do we provide fast, accurate AI-assisted synthesis over dense technical course notes while restricting retrieval strictly to the user-selected document context, enforcing semantic similarity cutoff thresholds, and returning exact page citations?
3. **Database Portability vs. Managed Cloud Services:** How can a full-stack application utilize high-dimensional vector embeddings and cloud object storage while preserving portable application-level authentication and maintaining local developer reproducibility?

---

## 4. What It Actually Does

### Resource Vault & Scoped RAG Assistant
- **Document Ingestion:** Users upload course PDFs tagged by subject and course codes. The backend extracts text page-by-page using `pypdf`, chunks the text using a recursive character splitting algorithm (1,000-character chunks with 200-character overlap), generates 768-dimensional vector embeddings via the Google Gemini API (`models/text-embedding-004`), and stores them in PostgreSQL using `pgvector`.
- **Scoped Question Answering:** Users open a document viewer and query the RAG assistant. The backend vectorizes the question, performs a Cosine Distance search (`<=>`) strictly bounded by `resource_id`, evaluates a similarity cutoff threshold ($0.65$), and synthesizes an answer using `gemini-1.5-flash` with exact page citations and source excerpts.
- **Doubt Board & Community Upvoting:** Resources feature threaded, nested discussion trees where users can post questions, reply to peers, mark answers as solved, and upvote quality contributions with denormalized counters.

### Peer-to-Peer Giveaway Marketplace
- **Classifieds & Filtering:** Users list physical study items (condition, photo, subject tag, pickup area). Prospective recipients browse active items using multi-parameter filters (subject, condition, pickup area).
- **Listing State Machine (`AVAILABLE` $\rightarrow$ `REQUESTED` $\rightarrow$ `GIVEN_AWAY`):**
  - An interested student submits a `ListingRequest`.
  - The item owner reviews pending requests on the Owner Dashboard.
  - When the owner clicks "Accept Request", a database transaction acquires an exclusive row-level lock (`select_for_update`) on the listing, verifies the status is still `AVAILABLE`, transitions the listing to `REQUESTED`, updates the request to `ACCEPTED`, and automatically rejects all competing pending requests.
  - If a handoff fails, the owner can cancel or withdraw the agreement, automatically returning the listing to `AVAILABLE`.
- **In-Process Notifications:** Dispatches transactional notifications to chosen recipients and competing requesters via Django `transaction.on_commit()` hooks.

---

## 5. Architecture

```
                                  StudyLink Monorepo
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
         frontend/ (React 18 SPA)                        backend/ (Django 5.1 REST API)
  ┌───────────────────────────────┐               ┌────────────────────────────────────────┐
  │ • Vite + Tailwind CSS         │               │ • config/ (Settings, URLs, WSGI/ASGI)  │
  │ • Zustand (Auth & Filters)    │ ◄─── REST ──► │ • accounts/ (CustomUser, SimpleJWT)    │
  │ • Axios (Token Interceptors)  │     JSON      │ • core/ (Subjects, Courses, Exceptions)│
  │ • react-pdf (Document Viewer) │               │ • vault/ (PDF Ingestion, Upvotes)      │
  │ • React Router 6              │               │ • rag/ (Gemini Client, pgvector Search)│
  └───────────────────────────────┘               │ • market/ (State Machine & Locking)    │
                                                  │ • notifications/ (In-app Event Inbox)  │
                                                  └───────────────────┬────────────────────┘
                                                                      │
                                        ┌─────────────────────────────┴─────────────────────────────┐
                                        ▼                                                           ▼
                           Supabase Managed Postgres                                   Supabase S3 Storage / Local
                    ┌──────────────────────────────────────┐                       ┌────────────────────────────────┐
                    │ • Relational Tables (UUID PKs)       │                       │ • Bucket: studylink-S3         │
                    │ • pgvector Extension (HNSW Indices)  │                       │ • Direct stream for PDFs &     │
                    │ • Transaction Pooler (Port 6543)     │                       │   listing photo uploads        │
                    └──────────────────────────────────────┘                       └────────────────────────────────┘
```

### Module Boundaries & Responsibilities
- `backend/accounts`: Custom user model inheriting from `AbstractBaseUser` with UUID primary keys; JWT issuance (15-minute access, 7-day HttpOnly refresh cookies); staged OAuth services.
- `backend/core`: Shared academic taxonomy (`Subject`, `Course` models with unique code slugs); custom global DRF exception handler (`custom_exception_handler`); standardized pagination (`StandardResultsSetPagination`).
- `backend/vault`: PDF metadata tracking; custom `ResourceStorage` layer routing to Supabase S3 or local disk; threaded `DoubtBoardComment` self-referential hierarchy.
- `backend/rag`: Integration with Google Gemini SDK; prompt engineering (`GROUNDING_PROMPT_TEMPLATE`); cosine distance queries; SQLite fallback compatibility layer (`CompatibleVectorField`, `CompatibleHnswIndex`).
- `backend/market`: Listing lifecycle domain logic (`accept_request`, `cancel_request`, `complete_listing`); state transition audit logs (`ListingStatusHistory`).
- `backend/notifications`: In-app notification dispatcher linked to transactional hooks.
- `frontend/src`: Modular component architecture with decoupled Zustand state slices (`authStore`, `filterStore`), protected route wrappers, dynamic PDF viewer, and RAG chat panel with citation jumping.

---

## 6. Important Technical Decisions

### Decision 1: Hand-Rolled Django Custom User & SimpleJWT over Supabase Auth
- **Context:** Supabase provides built-in Go-based authentication, which could have been integrated directly on the client.
- **Decision:** Implemented a custom Django user model (`accounts.CustomUser`) paired with `djangorestframework-simplejwt`.
- **Rationale:** 
  1. *Relational Ownership:* Academic user reputation, listing ownership, and discussion threads required first-class relational foreign keys within Django's ORM.
  2. *Vendor Independence:* Preserves full database portability, preventing vendor lock-in to Supabase-specific client SDKs.
  3. *Secure Credential Lifecycle:* Access tokens are stored in React memory while refresh tokens are stored in `HttpOnly`, `SameSite=Lax` cookies, protected by automatic Axios 401 request retry interceptors.

### Decision 2: Pessimistic Row Locking (`select_for_update`) for Marketplace Transitions
- **Context:** Multiple users can simultaneously submit requests for a single giveaway listing. If an owner reviews requests across multiple tabs or under high concurrency, two requests could be accepted concurrently.
- **Decision:** Wrapped state transitions inside `transaction.atomic()` and acquired an explicit row lock using `Listing.objects.select_for_update().get(id=listing_id)`.
- **Rationale:** Guaranteed that once a request acceptance transaction begins, no competing process can mutate the listing status until the first transaction commits or rolls back. Competing requests receive an explicit `HTTP 409 Conflict`.

### Decision 3: Document-Scoped Vector Retrieval with Hard Similarity Cutoff
- **Context:** General-purpose RAG systems often perform cross-document vector search, leading to irrelevant chunks being injected into prompts when a user wants specific answers from a single syllabus or lecture slide.
- **Decision:** 
  1. Scoped all similarity searches strictly to `resource_id == target_resource_id`.
  2. Implemented a similarity threshold gate: if the top retrieved chunk has a Cosine Similarity $< 0.65$ (Cosine Distance $> 0.35$), the system immediately short-circuits with a fallback response rather than calling the LLM.
- **Rationale:** Eliminates cross-document contamination, reduces unnecessary LLM API consumption on out-of-scope queries, and prevents hallucinated answers on documents lacking relevant text.

### Decision 4: Cross-Database Vector Compatibility Layer (PostgreSQL `pgvector` + SQLite Fallback)
- **Context:** PostgreSQL with `pgvector` is used for deployment and remote dev, but local unit testing and offline development benefit from standard SQLite.
- **Decision:** Built `CompatibleVectorField` and `CompatibleHnswIndex` in `vault/models.py`. When running on SQLite, vector fields store JSON string arrays and the search service executes an in-memory pure-Python Cosine Distance calculation (`calculate_python_cosine_distance`). On PostgreSQL, it uses native `VECTOR(768)` fields and the HNSW `<=>` operator.
- **Rationale:** Enables zero-setup unit testing and offline development while leveraging hardware-accelerated HNSW index searches in production PostgreSQL.

---

## 7. Interesting Engineering Problems

### 1. Concurrency Double-Claim Mitigation in Physical Giveaways
- **The Problem:** In a free giveaway exchange, race conditions occur when an owner accepts a request while another requester cancels or a second admin attempts an action.
- **Implementation:** In `market/services.py`, `accept_request` opens a database transaction, locks the target `Listing` row via `select_for_update()`, re-verifies that `status == 'AVAILABLE'`, updates status to `REQUESTED`, updates the chosen `ListingRequest` to `ACCEPTED`, bulk-rejects all other pending requests (`status='REJECTED'`), appends an immutable entry to `ListingStatusHistory`, and registers downstream notification dispatches via `transaction.on_commit()`.

### 2. Recursive PDF Chunking with Page Citation Tracking
- **The Problem:** Generic string chunkers split text across fixed character lengths, breaking across page boundaries and destroying the ability to cite exact page numbers in AI responses.
- **Implementation:** In `vault/services.py`, `PDFIngestionService` iterates page-by-page using `pypdf.PdfReader`. Within each page, `recursive_split` hierarchically segments text across structural separators (`\n\n`, `\n`, `' '`, `''`), enforcing a maximum chunk size of 1,000 characters with a 200-character overlapping sliding window. Each chunk retains its 1-indexed `page_number`, which flows directly through vector storage to the frontend citation badges.

### 3. Axios Interceptor Queue for HttpOnly JWT Silent Refresh
- **The Problem:** When an access token expires in React, multiple parallel API requests simultaneously fail with HTTP 401, triggering multiple redundant refresh calls and race conditions in state management.
- **Implementation:** In `frontend/src/hooks/useApi.js`, an Axios response interceptor maintains an `isRefreshing` lock and a `failedQueue` array. The first 401 request triggers `/api/v1/auth/token/refresh/` using the HttpOnly cookie. Subsequent 401 requests return pending promises pushed into `failedQueue`. Once the new access token is received, the queue is drained and retried with the updated authorization header.

---

## 8. Failure Modes / Things That Went Wrong

1. **Test Runner Memory & Mock Assertions under Python 3.14 Pre-Release:**
   - *Failure:* Django 5.1's test client encountered an `AttributeError: 'super' object has no attribute 'dicts'` in `template/context.py` when running full suite tests under Python 3.14 pre-release due to changes in CPython's `copy.py` mechanism.
   - *Resolution:* Verified application business logic directly via targeted app-level test suites and mocked API client tests.
2. **Local PDF Embedding Blocked by Default Security Headers:**
   - *Failure:* Embedding uploaded PDF files inside the React frontend's `<PdfViewer>` iframe was initially blocked by Django's `XFrameOptionsMiddleware` returning `X-Frame-Options: DENY`.
   - *Resolution:* Adjusted frame options middleware configuration for local media endpoints while preserving secure headers on production API routes.
3. **S3 Mock Configuration in Asynchronous Unit Tests:**
   - *Failure:* Unit tests executing vault uploads without explicit S3 mocks attempted direct network calls to Supabase S3 endpoints, throwing `botocore.exceptions.ClientError`.
   - *Resolution:* Patched `django.core.files.storage.default_storage` and `ResourceStorage` across unit tests to isolate test runs from live cloud credentials.

---

## 9. Verification / Testing

### Automated Test Architecture
- **Backend Test Suite (Django / Python):**
  - `accounts/tests`: Validates CustomUser creation, JWT token issuance, refresh token rotation, and OAuth callback verification.
  - `core/tests`: Tests academic tag endpoints, subject/course filtering, pagination limits, and custom exception JSON formatting.
  - `market/tests`: Tests listing CRUD, request creation, state machine transitions, concurrent `select_for_update` locking guards, and status audit logging.
  - `vault/tests`: Tests PDF upload validation, upvoting toggle logic, threaded comment creation/parent-child validation, and edge cases.
  - `rag/tests`: Tests `recursive_split` character bounds, Gemini mock client embeddings, SQLite vector fallback distance calculations, and cutoff threshold enforcement.
  - `notifications/tests`: Tests synchronous event triggers, inbox queries, and read status toggles.
- **Frontend Test Suite (Vitest / React Testing Library):**
  - `authStore.test.js`: Validates authentication state mutations, login, logout, and token retention.
  - `components.test.jsx`: Tests `Button`, `Badge`, `Card`, `UpvoteButton`, `DoubtBoard`, and `RagChatPanel` rendering and event handling.
  - `routing.test.jsx`: Tests `ProtectedRoute` navigation guards and unauthenticated redirect paths.
  - `useApi.test.js`: Tests Axios interceptor base URL handling and authorization header injection.
- **End-to-End Test Suite (Playwright):**
  - `auth_flow.spec.js`: Simulates registration, login, protected navigation, and logout.
  - `market_state.spec.js`: Simulates a multi-user giveaway scenario: item creation, request submission, owner dashboard review, request acceptance, and handoff completion.
  - `vault_rag.spec.js`: Simulates PDF document upload, status polling, opening document viewer, asking AI questions, and verifying page citations.
  - `smoke.spec.js`: Verifies critical routing, navigation, and responsiveness across viewports.

---

## 10. Deployment

- **Backend Containerization:** Production `backend/Dockerfile` based on `python:3.12-slim` configured to execute Gunicorn WSGI (`config.wsgi:application`) on port 8080.
- **Production Settings Override:** `backend/config/settings_prod.py` configured with `SECURE_PROXY_SSL_HEADER`, strict CORS regex matching (`*.vercel.app`), SSL redirects, and HSTS headers for Google Cloud Run deployment.
- **Frontend Deployment Configuration:** Monorepo root `vercel.json` configured for automated Vite production builds (`cd frontend && npm run build` outputting to `frontend/dist`) with single-page app wildcard routing rewrites.
- **Deployment Status:** **Intentionally Deferred (v1).** The repository is maintained as a fully containerized, locally runnable codebase. Live cloud hosting is deferred to avoid sleeping free-tier instance cold starts and billing overhead.

---

## 11. What I Learned

1. **State Machine Modeling:** Modeling critical business workflows (like item handoffs) as an explicit, enumerable state machine with database-level row locks is vastly superior to scattered boolean flags across multiple models.
2. **RAG Boundary Enforcement:** A successful RAG implementation is defined as much by its rejection criteria (filtering out-of-scope context and applying similarity cutoff thresholds) as by its generative quality.
3. **Decoupled Architecture Payoffs:** Implementing a clean REST contract and separating domain models into distinct Django apps allowed backend data logic and frontend SPA components to evolve independently without circular dependencies.

---

## 12. What Changed in My Thinking

- **Before:** Assumed cloud-hosted SaaS tools (like Supabase Auth or third-party vector databases) should always be used to maximize development speed.
- **After:** Realized that managing identity and vector tables directly within the application's relational database (Django + PostgreSQL `pgvector`) provides greater schema flexibility, enables atomic transactional joins, eliminates vendor lock-in, and significantly simplifies testing.

---

## 13. Distinctive / Interesting Details

- **"Contextual Duality" UI Design System:** The application uses distinct visual metaphors for its two modules: the **Resource Vault** adopts a dense, structured "Library" feel for focused study, while the **Marketplace** adopts a visual, card-based "Campus Square" feel for quick physical item discovery.
- **Pure-Python Vector Fallback:** The custom `CompatibleVectorField` enables local testing on SQLite without requiring external vector database services or Dockerized PostgreSQL during quick unit test runs.
- **Exact Citation Jumping:** Source excerpts returned by the RAG pipeline include exact page numbers that link directly to corresponding PDF pages in the embedded React document viewer.

---

## 14. Skills Demonstrated

### Engineering Skills
- Relational Database Modeling & ACID State Machine Design
- Concurrency Management with Pessimistic Row Locking (`select_for_update`)
- Retrieval-Augmented Generation (RAG) Architecture & Vector Embeddings
- RESTful API Design, Error Formatting & Pagination
- Authentication Architecture (JWT Access/Refresh Tokens & HttpOnly Cookies)
- Monorepo Architecture & Production Containerization (Docker, Gunicorn)
- Automated Testing (Unit, Component, and End-to-End Integration)

### Technologies & Tools
- **Backend:** Python 3, Django 5.1, Django REST Framework, SimpleJWT, Celery, Gunicorn, `pypdf`
- **Database & Storage:** PostgreSQL, `pgvector`, SQLite, Supabase Storage (S3 API)
- **Frontend:** React 18, Vite, Tailwind CSS, Zustand, Axios, `react-pdf`, React Router 6
- **AI / LLM:** Google Gemini API (`text-embedding-004`, `gemini-1.5-flash`)
- **Testing & Tooling:** Pytest / Django TestCase, Vitest, React Testing Library, Playwright, Docker, Oxlint

### Concepts
- Pessimistic Concurrency Control
- Vector Similarity Search (Cosine Distance / HNSW Indexing)
- Grounded Prompt Engineering & Hallucination Guardrails
- Transactional Event Hooks (`transaction.on_commit`)
- Silent Token Refresh Interceptor Patterns
- Cross-Database Abstraction Layers

### Best Skills for LinkedIn
1. **Django REST Framework**
2. **PostgreSQL / pgvector**
3. **Retrieval-Augmented Generation (RAG)**
4. **React.js / Zustand**
5. **Database Concurrency & Locking**
6. **Docker & Containerization**
7. **REST API Architecture**
8. **Python**

---

## 15. Public Content

### LinkedIn Project Description
University study materials and physical textbooks often end up scattered across unindexed group chats and chaotic classifieds. I built **StudyLink**, a full-stack academic resource and peer-to-peer giveaway platform designed around two distinct engineering problems: document-scoped AI retrieval and concurrent state integrity.

On the digital side, StudyLink features a **Resource Vault** with an integrated **RAG assistant**. When students upload course PDFs, the backend extracts text page-by-page, generates 768-dimensional embeddings using the Google Gemini API, and indexes them in PostgreSQL using `pgvector`. When querying their notes, similarity search is strictly scoped to the active document and gated by a cosine similarity cutoff threshold ($0.65$) to eliminate hallucinations on out-of-scope questions, returning grounded answers alongside exact page citation excerpts in an embedded PDF viewer.

On the physical side, the **Giveaway Marketplace** coordinates local textbook and equipment handoffs using a formal **Listing State Machine** (`AVAILABLE` $\rightarrow$ `REQUESTED` $\rightarrow$ `GIVEN_AWAY`). To prevent race conditions when multiple students request the same item, request acceptance is protected by database-level pessimistic row locking (`select_for_update`) inside atomic transactions, automatically rejecting competing claims and dispatching in-process notifications via `transaction.on_commit()` hooks.

The project is built with **Django REST Framework**, **PostgreSQL (`pgvector`)**, **React 18 (Vite)**, **Zustand**, and **Tailwind CSS**, fully containerized with Docker and verified across unit and Playwright integration test suites.

### LinkedIn Featured Description
*(Deployment note: Public cloud hosting is intentionally deferred for the v1 release to prioritize local container reproducibility; no live public URL is currently active.)*

### Resume Bullet 1 / 2 / 3
- **Bullet 1 (RAG & Vector Search):** Built a document-scoped RAG pipeline in Django and PostgreSQL (`pgvector`), utilizing Gemini `text-embedding-004` (768-dim) and `gemini-1.5-flash` with a $0.65$ cosine similarity cutoff threshold to provide grounded Q&A with exact PDF page citations.
- **Bullet 2 (Concurrency & State Machine):** Engineered an ACID-compliant Marketplace state machine (`AVAILABLE` $\rightarrow$ `REQUESTED` $\rightarrow$ `GIVEN_AWAY`) utilizing PostgreSQL pessimistic row locking (`select_for_update`) in atomic transactions to prevent double-claim race conditions during concurrent item requests.
- **Bullet 3 (Full-Stack Architecture & Auth):** Developed a modular React 18 SPA and Django REST API featuring JWT authentication with HttpOnly refresh cookie rotation, Zustand state management, and an automated Playwright E2E test suite simulating end-to-end user handoff lifecycles.

### GitHub Repo One-Liner
Full-stack academic vault with pgvector Gemini RAG and a concurrent peer-to-peer giveaway marketplace.

---

## 16. Claims That Should NOT Be Made

- **Do NOT claim live production user adoption, active student count, or university partnerships** (e.g. "Used by 500+ students at university").
- **Do NOT claim cloud scale or high throughput metrics** (e.g. "Processes 10,000 QPS with 99.99% uptime").
- **Do NOT claim live production hosting** (cloud hosting on Cloud Run/Vercel was evaluated and configured, but intentionally deferred for v1 release).
- **Do NOT claim real-time WebSockets / Celery background workers are active in v1** (Celery worker tasks are staged for v2; v1 executes PDF ingestion and notifications synchronously via in-process transaction hooks).
- **Do NOT claim social OAuth (Google/GitHub) is active in the v1 frontend UI** (the backend OAuth endpoints are built and tested, but social login buttons were deferred to v2 in the v1 UI).

---

## 17. Evidence / Source References

- **RAG Implementation & Cosine Distance Fallback:** [backend/rag/search.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/rag/search.py#L23-L115), [backend/rag/client.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/rag/client.py), [backend/rag/prompt.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/rag/prompt.py).
- **Listing State Machine & Pessimistic Locking:** [backend/market/services.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/market/services.py#L13-L81), [backend/market/models.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/market/models.py).
- **PDF Extraction & Recursive Splitting:** [backend/vault/services.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/vault/services.py#L3-L65).
- **Custom User & JWT Authentication:** [backend/accounts/models.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/accounts/models.py), [backend/accounts/views.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/accounts/views.py), [frontend/src/store/authStore.js](file:///d:/Coding/Projects----For%20Resume/StudyLink/frontend/src/store/authStore.js).
- **Axios Refresh Queue Interceptor:** [frontend/src/hooks/useApi.js](file:///d:/Coding/Projects----For%20Resume/StudyLink/frontend/src/hooks/useApi.js#L41-L94).
- **Database Schema & Relational Models:** [Docs/DB_Schema.md](file:///d:/Coding/Projects----For%20Resume/StudyLink/Docs/DB_Schema.md), [backend/vault/models.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/vault/models.py).
- **Deployment Profiles & Docker Setup:** [backend/Dockerfile](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/Dockerfile), [backend/config/settings_prod.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/config/settings_prod.py), [vercel.json](file:///d:/Coding/Projects----For%20Resume/StudyLink/vercel.json).
- **E2E Integration Verification:** [tests/e2e/market_state.spec.js](file:///d:/Coding/Projects----For%20Resume/StudyLink/tests/e2e/market_state.spec.js), [tests/e2e/vault_rag.spec.js](file:///d:/Coding/Projects----For%20Resume/StudyLink/tests/e2e/vault_rag.spec.js), [tests/e2e/auth_flow.spec.js](file:///d:/Coding/Projects----For%20Resume/StudyLink/tests/e2e/auth_flow.spec.js).
- **Scope Deferral Backlog:** [Docs/Backlog_v2.md](file:///d:/Coding/Projects----For%20Resume/StudyLink/Docs/Backlog_v2.md), [README.md](file:///d:/Coding/Projects----For%20Resume/StudyLink/README.md).

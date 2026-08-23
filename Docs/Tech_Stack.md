# Tech_Stack.md — StudyLink

This document defines the technical specifications and infrastructure for **StudyLink**. The stack is selected to demonstrate proficiency in integrating high-level web frameworks (Django/React) with specialized AI services and cloud-native deployment patterns.

---

## 1. Backend Orchestration (Django)

| Technology | Version | Rationale |
| :--- | :--- | :--- |
| **Python** | `3.12` | Leverages modern type hinting and performance improvements for async-aware code. |
| **Django** | `5.0` | Utilizes the latest ORM features and native support for asynchronous database operations where needed. |
| **Django REST Framework** | `3.15` | Provides the industry-standard toolkit for building the platform's Web APIs. |
| **JWT Auth** | `SimpleJWT` | Decentralizes session management for v1, allowing the frontend to keep the access token in memory and the refresh token in an `HttpOnly` cookie. |
| **App Structure** | `accounts`, `vault`, `market`, `core` | Separates domain logic into distinct apps: `vault` for digital, `market` for physical, and `core` for shared Subject/Course tags. |

---

## 2. Database & Storage (Supabase)

| Technology | Version | Rationale |
| :--- | :--- | :--- |
| **Supabase Postgres** | `15.x` | Provides a managed PostgreSQL instance with `pgvector` pre-installed, reducing infra overhead while keeping SQL power. |
| **Connection Pattern** | `psycopg` + Pooler | Django connects via the Supabase Transaction Pooler (port 6543) to handle the short-lived connections typical of containerized environments. |
| **pgvector** | `0.5.x` | Enables efficient vector similarity searches within SQL queries to support the Chat-with-notes feature. |
| **Supabase Storage** | `S3-Compatible` | Used for PDFs and listing photos; integrated via `django-storages` (S3 backend) to route all `FileField` saves directly to the cloud. |

---

## 3. Frontend Client (React)

| Technology | Version | Rationale |
| :--- | :--- | :--- |
| **React** | `18.x` | Uses the stable concurrent renderer for a fluid UI during heavy filtering or AI streaming. |
| **Vite** | `5.x` | Modern build tool providing near-instant Hot Module Replacement (HMR) and optimized production bundles. |
| **State Management** | `Zustand` | Lightweight store that handles user auth state and marketplace filters without the boilerplate of Redux. |
| **Routing** | `React Router 6` | Manages the distinct `/vault` and `/marketplace` paths while persisting the `FilterSidebar` across module transitions. |
| **Styling** | `Tailwind CSS` | Utility-first approach for rapid construction of the "Owner Dashboard" and "Resource Grid" layouts. |

---

## 4. AI & Retrieval Layer (Gemini)

| Technology | Version | Rationale |
| :--- | :--- | :--- |
| **LLM / Embeddings** | `Gemini 1.5 Flash` | Offers the best balance of speed and large context window for summarizing student notes at no/low cost. |
| **Embedding Model** | `text-embedding-004` | High-performance model specifically optimized for technical and academic text retrieval. |
| **Chunking** | `RecursiveCharacter` | Splits PDFs by structural markers (paragraphs, newlines) via LangChain to maintain context in dense notes. |
| **Query Pattern** | `Cosine Similarity` | Uses `pgvector` to perform `<=>` similarity searches scoped to a single `resource_id` in the `resource_chunks` table. |

---

## 5. Deployment & CI/CD

| Component | Platform | Strategy |
| :--- | :--- | :--- |
| **Backend** | `Google Cloud Run` | Django is containerized for a serverless, auto-scaling deployment using Cloud Run's default `*.run.app` URL. |
| **Frontend** | `Vercel` | Optimized for React SPAs; hosted on Vercel's default deployment URL with edge-caching. |
| **Processing Pattern** | `Synchronous` | Ingestion, chunking, and vector embedding run synchronously within the HTTP upload request cycle for v1. |
| **CI/CD** | `GitHub Actions` | Automatically builds the Docker image on push, pushes to Google Artifact Registry, and triggers a Cloud Run revision. |

---

## 6. Local Development Infrastructure

| Strategy | Rationale |
| :--- | :--- |
| **Hybrid Local/Cloud** | **Approach:** Local Django + Local React connecting to a remote Supabase Dev Project. |
| **Rationale** | Running a local Dockerized Postgres with `pgvector` and an S3-compatible storage emulator (like MinIO) adds significant local setup friction. Using a dedicated Supabase "Dev" environment ensures the DB schema, storage buckets, and vector extensions are identical to production with zero local configuration. |

---

## 7. Architectural Rationale: The "Interview" Defense

### Why hand-roll Django Auth + JWT instead of using Supabase Auth?

While Supabase Auth is convenient, I chose **Django + SimpleJWT** for two strategic reasons:

1.  **Ownership of the User Model:** In a platform like StudyLink, the `User` is the core of everything—marketplace reputation, resource ownership, and academic profiles. Storing users in Django's internal DB allows me to leverage the full power of the Django ORM for complex joins and signals (e.g., notifying requesters when an item is gone).
2.  **Portability:** This approach prevents "Vendor Lock-in." By keeping the Auth logic inside the application code, the project remains portable to any Postgres provider, rather than being coupled to Supabase’s proprietary Go-based Auth service.

### Scope Deferred to v2 Backlog

*   **OAuth Integration (Google & GitHub):** Google/GitHub OAuth consent-screen setup and callback URI management were the slowest, least-automatable parts of a prior deployment; deferred to v2 backlog.
*   **Async Processing (Celery + Redis):** Celery worker configuration and Redis broker provisioning were the slowest, least-automatable parts of a prior deployment; PDF ingestion and embedding generation run synchronously in v1, deferred to v2 backlog.
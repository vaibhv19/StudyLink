# PRD.md — StudyLink

**Project Name:** StudyLink  
**Status:** Architecture & Implementation Phase  
**Document Version:** 1.1 (v1 Scope Trimmed)

---

## 1. Problem Statement

StudyLink addresses two distinct frictions within the academic lifecycle where resources are consistently underutilized or lost:

1.  **Digital Fragmentation (Resource Vault):** Quality study materials—lecture notes, summaries, and exam prep—are scattered across ephemeral WhatsApp groups, Discord servers, and personal drives. Discovery is difficult, and there is no centralized, searchable repository that allows students to interact deeply with the content.
2.  **Physical Wastage (Giveaway Marketplace):** Physical textbooks and lab equipment often go to waste after a semester. Existing marketplaces (like OLX or eBay) are cluttered with commercial listings or require complex shipping/payment logistics. There is no dedicated local-only platform for students to pass physical goods directly to the next cohort without friction.

---

## 2. Target User & Use Case

**Target Persona:** Technical Recruiters and Engineering Managers.  
**Core Use Case:** As a portfolio piece, StudyLink demonstrates the ability to architect and deploy a multi-module full-stack application. It showcases:
*   **Django Proficiency:** Complex data modeling, state machine implementation, and JWT auth integration.
*   **React Competency:** Responsive filtering, dashboard state management, and real-time AI chat interfaces.
*   **Modern AI Integration:** Implementing a scoped RAG (Retrieval-Augmented Generation) pipeline using Gemini and `pgvector`.
*   **System Reliability:** Handling file uploads, status transitions, and secure multi-tenant resource access.

---

## 3. In-Scope Features

### 3.1 Module 1: Resource Vault (Digital)
*   **Digital Repository:** Upload and storage of PDFs and notes tagged by subject, course, and academic year.
*   **Search & Discovery:** Multi-parameter filtering (subject/tags) to surface relevant materials.
*   **Community Validation:** A rating/upvote system to ensure high-quality resources rise to the top.
*   **Chat-with-Notes (RAG):** A dedicated interface allowing users to select a specific PDF and ask technical questions. The system performs similarity searches over that document’s chunks to provide context-aware answers.

### 3.2 Module 2: Giveaway Marketplace (Physical)
*   **Listing Management:** Users can list items with titles, condition reports, subject tags, and pickup_area descriptions.
*   **State-Machine Lifecycle:** Listings follow a strict flow: `Available → Requested → Given Away`. Items can fall back to `Available` if a handoff fails.
*   **Owner Dashboard:** A centralized view for users to manage their active listings and review pending requests from interested students.
*   **Handoff Coordination:** A request system where owners choose a recipient, and all other requesters are notified once the item is claimed.

### 3.3 Backend Layer (Django)
*   **Authentication:** JWT Auth (Access/Refresh Tokens) for local email/password accounts in v1 (OAuth integration deferred to v2).
*   **Storage Integration:** Managing PDF and image uploads to Supabase Storage.
*   **Vector Operations:** Handling text chunking and storing embeddings in Supabase Postgres via `pgvector` (processed synchronously during upload in v1).
*   **Notification Engine:** Triggering system notifications for request updates and marketplace status changes.

### 3.4 Frontend Layer (React)
*   **Contextual UI:** Two distinct visual zones for the Vault and the Marketplace with shared navigation.
*   **Filtering Interface:** A unified sidebar/search bar for subject-based resource discovery.
*   **RAG Interface:** A chat bubble UI that displays LLM answers alongside source excerpts from the document.

---

## 4. Explicit Non-Goals

*   **No Commercial Transactions:** No payment gateway (Stripe/PayPal) integration. This is a "giveaway" platform.
*   **No Shipping Logistics:** The platform is strictly for local pickup; no address verification or shipping label generation.
*   **Single-Document RAG Only:** The "Chat-with-Notes" feature is scoped to the active document only. No cross-document retrieval or global knowledge-base queries.
*   **No Automated Matching:** No "Recommendation Engine" or "Smart Match" algorithm for v1; discovery is purely search/filter-based.
*   **No Public Cloud Deployment in v1:** Active deployment to GCP Cloud Run / Vercel is intentionally deferred; the project is maintained as a locally runnable repository with complete containerization readiness.
*   **No OAuth in v1:** Google and GitHub OAuth social login and account linking are deferred to v2.
*   **No Async Background Workers in v1:** Celery and Redis worker queues are deferred to v2.

---

## 5. Success Criteria

*   **Lifecycle Integrity:** A marketplace listing must correctly transition through all states (Available/Requested/Given Away) without data corruption or orphaned requests.
*   **Retrieval Accuracy:** The RAG system must correctly identify and cite a specific page or chunk from an uploaded PDF when queried about its contents.
*   **Auth Reliability:** Users must be able to securely register, log in, and maintain sessions via JWT.
*   **Asset Management:** PDF and Image uploads must reliably persist in Supabase Storage with correct owner permissions.

---

## 6. Key Risks & Considerations

*   **OCR/Handwritten Notes:** The quality of the RAG feature is highly dependent on the readability of uploaded PDFs. There is a risk of poor answer quality or hallucinations when users upload low-contrast, handwritten technical notes.
*   **Request Concurrency:** Managing multiple simultaneous requests for a single physical item to ensure the owner doesn't accidentally "double-commit" a handoff.
*   **Gemini Context Limits:** Managing large PDFs that may exceed the prompt context window if chunking and retrieval aren't precisely tuned.
*   **v1 Upload Latency:** Synchronous PDF ingestion and vector generation means response time scales with file size, accepted as a v1 tradeoff.
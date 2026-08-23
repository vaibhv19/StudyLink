# RAG_Chat_Feature.md — Scoped Chat-with-Notes

This document defines the technical architecture for the "Chat-with-notes" feature in StudyLink. While it utilizes Retrieval-Augmented Generation (RAG), its design is deliberately scoped to support student productivity within a single-document context, rather than acting as a wide-scale technical knowledge base.

---

## 1. Explicit Scope Boundary: Single-Document Focus

Unlike comprehensive RAG systems that query across an entire library, StudyLink’s retrieval is strictly restricted to **one `resource_id` per chat session.**

*   **Design Choice:** Single-document retrieval.
*   **Rationale:** In an academic setting, students typically study one specific chapter or lecture set at a time. Searching across a whole corpus introduces "inter-document noise"—where a term from a Biology PDF might pollute a query about a Chemistry PDF. By scoping the search to one document, we achieve high precision and lower latency without the need for complex hybrid search. 
*   **Airtight Boundary:** This is not a technical limitation; it is a feature designed for **Information Focus**, mirroring the Marketplace’s "Local-Only" boundary designed for **Community Focus**.

---

## 2. Ingestion & Chunking Strategy

Chunking and embedding occur **synchronously** within the upload HTTP request cycle upon file upload to Supabase Storage.

*   **Timing:** Executed synchronously in the Django request handler immediately after saving the PDF file.
*   **Splitter:** `RecursiveCharacterTextSplitter`.
*   **Parameters:** 
    *   **Chunk Size:** 1,000 characters.
    *   **Chunk Overlap:** 200 characters.
*   **Rationale:** Academic notes often contain dense definitions and examples. A 1,000-character window is wide enough to capture a full definition plus its surrounding context, while the 200-character overlap prevents the loss of meaning at the split boundaries.
*   **v1 Tradeoff & Limitation:** Upload response time scales directly with PDF size (e.g. text extraction and vector generation take a few extra seconds for large PDFs). This is an accepted v1 scope limitation to avoid Redis/Celery deployment complexity, and is flagged as a candidate for background processing offloading in v2.

---

## 3. Embedding Generation & Vector Storage

StudyLink leverages the Google Gemini ecosystem for both vectorization and response synthesis.

*   **Embedding Model:** `text-embedding-004` (768 dimensions).
*   **Storage:** `resource_chunks` table in Supabase Postgres.
*   **Schema:**
    | Column | Type | Role |
    | :--- | :--- | :--- |
    | `id` | `UUID` | Primary Key |
    | `resource_id` | `UUID` | FK to `Resource` (The parent PDF) |
    | `content` | `TEXT` | The raw text of the chunk |
    | `page_number` | `INT` | Extracted from PDF metadata for citations |
    | `embedding` | `VECTOR(768)` | The generated semantic vector |

---

## 4. Query Flow (The Retrieval Loop)

1.  **Request:** React frontend sends the user's question + `resource_id` to `POST /api/v1/chat/query/`.
2.  **Vectorization:** Django calls Gemini to embed the user's question.
3.  **Scoped Search:** Django executes a Cosine Similarity search using the `pgvector` `<=>` operator with a hard filter: `WHERE resource_id = [Target_ID]`.
4.  **Top-K Retrieval:** The system retrieves the Top-5 most relevant chunks.
5.  **Synthesis (Grounding):** Chunks are injected into a prompt: *"Using only the following excerpts from a student's notes, answer the question: [Question]. If the answer isn't in the excerpts, say you don't know."*
6.  **Response:** The backend returns the generated answer plus the `page_number` and `content` of the retrieved chunks.

---

## 5. Failure Modes & Graceful Handling

StudyLink implements specific guardrails for academic document edge cases:

*   **Failure 1: The "Scanned Image" PDF.** If the PDF contains no extractable text (un-OCR'd scan), the ingestion pipeline marks the resource as `UNSEARCHABLE`. The chat UI is disabled for this resource, and a message appears: *"This document appears to be an image. Use an OCR tool to make it searchable."*
*   **Failure 2: The "Out of Bounds" Question.** If the Top-1 chunk's similarity score is below a threshold (e.g., `0.65`), the system aborts LLM generation.
    *   **Action:** Returns a standardized refusal: *"I couldn't find any relevant information in this specific document to answer that. Try checking your other resources or the Doubt Board."*
    *   **Rationale:** This prevents hallucinations and reinforces the "Single-Document" scope boundary.

---

## 6. Contrast: StudyLink vs. Phoenix

While both projects utilize RAG, they serve fundamentally different architectural goals:

1.  **Conceptual Alignment:** Both use chunking, embeddings (`pgvector`), and LLM grounding to provide source-backed answers.
2.  **Deliberate Simplicity:** StudyLink ignores **Hybrid Search (BM25)**. In Phoenix, hybrid search is necessary to find exact error codes in a massive technical corpus. In StudyLink, semantic search is sufficient because the search space is limited to a single document.
3.  **Deterministic vs. Heuristic:** Phoenix uses a complex **Fallback State Machine** (rewriting/re-ranking) to recover weak searches. StudyLink uses a **Binary Relevance Check**—if the answer isn't in the chunks, it stops. This prioritizes speed and cost-efficiency for a student-facing tool.
4.  **UX Goal:** Phoenix aims for **Transparency** (showing the reasoning trace). StudyLink aims for **Directness** (getting a quick answer for a specific exam topic).
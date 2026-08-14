# Phase 07 — Gemini RAG Ingestion & API

This phase implements the retrieval-augmented generation (**RAG**) pipeline scoped strictly to a single document. It covers PDF text parsing, recursive chunking, Google Gemini embedding generation, pgvector Cosine Similarity query matching, citation mappings, and the final Chat Query API endpoint.

---

## 1. Module Design: `rag` Integration (Shared between `vault` and core)

### 1.1 Folder Structure
```text
backend/vault/
├── tasks.py                    # Celery ingestion task implementation
├── services.py                 # Ingestion, chunking, and embedding services
backend/config/
├── settings.py                 # Gemini configurations and pgvector requirements
backend/market/ (unaffected)
backend/rag/                    # Dedicated folder for RAG specific helpers
    ├── __init__.py
    ├── client.py               # Gemini Client initializer
    ├── search.py               # Similarity search queries using pgvector
    ├── prompt.py               # Grounding templates configurations
    ├── views.py                # POST /api/v1/chat/query/ View
    ├── urls.py                 # RAG URL routing
    └── tests/
        ├── __init__.py
        ├── test_splitter.py    # Text splitter unit tests
        ├── test_vector.py      # pgvector mock queries tests
        └── test_chat_api.py    # LLM Mock integration API tests
```

### 1.2 Purpose
Ingests student notes into a vector database and answers technical questions about an uploaded PDF by retrieving relevant passages.

### 1.3 Dependencies
- `google-generativeai` (Gemini SDK)
- `pypdf` (lightweight PDF parsing utility)
- `pgvector` (django integrations or raw SQL cursor wrapper)
- `vault` app (for resource lookup validation)

### 1.4 Inputs
- Raw PDF files streamed from storage.
- User queries linked to specific resource IDs.

### 1.5 Outputs
- Segmented text chunks and 768-dimensional floats arrays in `resource_chunks`.
- Citation-backed text answers returned to the client.

### 1.6 Classes, Methods & Serialization Mappings

#### Model: `ResourceChunk` (in `vault/models.py`)
- **Fields:**
  - `id`: `models.UUIDField` (default `uuid.uuid4`, primary key)
  - `resource`: `models.ForeignKey` (`Resource`, on_delete=models.CASCADE, related_name="chunks")
  - `content`: `models.TextField`
  - `page_number`: `models.IntegerField`
  - `embedding`: `VectorField(dimensions=768)` (using pgvector HNSW indexing)

#### Services & Classes:
- `rag.client.GeminiClient`: Wraps generativeai setup and embedding requests.
- `vault.services.PDFIngestionService`: Orchestrates downloading, text extraction, character splitting, and database indexing.
- `rag.search.VectorSearchService`: Performs similarity calculations and applies the similarity threshold cutoff.

#### Prompt Grounding Template:
```text
You are an academic AI assistant. Using only the following text excerpts from a student's notes, answer the question: {query}.

Excerpts:
{context}

Guidelines:
1. Provide a direct, concise, and structured answer.
2. Cite the source page numbers (e.g., "[Page X]") when referencing facts.
3. If the answer cannot be determined from the excerpts, state: "I couldn't find any relevant information in this specific document to answer that."
```

---

## 2. Implementation Tasks

### 2.1 Django Backend Layer (`backend/`)

#### Feature: PDF Parsing & Ingestion Task
Extract notes text and split it into chunks.

##### Task 07.01.01: Implement PDF Ingestion & Text Splitting Service
- **Estimated Size:** M
- **Risk:** Medium
- **Prerequisites:** Phase 06 complete
- **Task Description:** Write a service method `extract_and_split_pdf(file_stream)`. Use `pypdf` to extract text page-by-page. Implement a recursive splitter parsing text into chunks of 1,000 characters with 200 character overlaps, keeping page numbers attached to each chunk.
- **Definition of Done:**
  - Mocking file streams yields structured lists of chunks containing page metadata and text.
  - Returns empty results if the PDF contains zero extractable text (e.g., scanned images).

##### Task 07.01.02: Configure Gemini SDK Client
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Phase 01 complete
- **Task Description:** Write a client initialization wrapper in `rag/client.py`. Read `GEMINI_API_KEY` from settings. Add helper functions to query embedding vectors using model `text-embedding-004`.
- **Definition of Done:**
  - Querying the helper function returns 768-dimensional float arrays.
  - Handles API quota rate-limit exceptions gracefully.

##### Task 07.01.03: Build Ingestion Celery Task Workflow
- **Estimated Size:** M
- **Risk:** Medium
- **Prerequisites:** Task 07.01.01, Task 07.01.02
- **Task Description:** Fully implement `process_pdf_document_task` in `vault/tasks.py`. The task must download the PDF from Supabase, parse it, fetch embeddings for each chunk, and save them in the `ResourceChunk` database model. Update resource state to `READY` on success, `UNSEARCHABLE` if no text is found, or `FAILED` if an unhandled error occurs.
- **Definition of Done:**
  - Running the task processes a sample PDF, populates the chunks database table, and marks the resource status as `READY`.

#### Feature: Similarity Search & Prompt Grounding
Build the vector query backend.

##### Task 07.01.04: Implement pgvector Cosine Similarity Search
- **Estimated Size:** M
- **Risk:** High
- **Prerequisites:** Task 07.01.03
- **Task Description:** Implement similarity searches in `rag/search.py`. Write a database query using pgvector's `<=>` (Cosine Distance) operator:
  - Select chunks where `resource_id = TargetID`.
  - Calculate distance to user query vector.
  - Return the top 5 chunks.
- **Definition of Done:**
  - Querying the database returns matching chunks sorted by distance.

##### Task 07.01.05: Implement Binary Cutoff & Grounding Generation Service
- **Estimated Size:** M
- **Risk:** Medium
- **Prerequisites:** Task 07.01.04
- **Task Description:** Write a generation service. Calculate similarity score (`1 - CosineDistance`). If the top chunk's similarity score is below `0.65`, bypass LLM synthesis and return the standard rejection response. Otherwise, construct the prompt, call `gemini-1.5-flash` to synthesize the answer, and structure source page numbers in a citations list.
- **Definition of Done:**
  - Weak queries trigger the cutoff and return the standard fallback response without calling the LLM.
  - Strong queries return a cited answer referencing matching database pages.

##### Task 07.01.06: Implement Chat API View
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 07.01.05
- **Task Description:** Create `POST /api/v1/chat/query/` routing to `rag/views.py`. Validate input parameters `resource_id` (must exist and be `READY`) and `query` string. Return JSON containing the answer and sources citations.
- **Definition of Done:**
  - Valid requests return cited answers.
  - Requests for processing or failed resources return a HTTP 400 Bad Request.

##### Task 07.01.07: Write RAG Pipeline Integration Tests
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Task 07.01.06
- **Task Description:** Write test cases in `rag/tests/`. Mock Gemini API calls using unittest.mock. Validate chunking bounds, similarity scores, and API exception routes.
- **Definition of Done:**
  - Pytest runs without errors.

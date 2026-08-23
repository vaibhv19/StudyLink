# Phase 06 — Background Processing `[DEFERRED TO V2 / SKIPPED FOR V1]`

> [!IMPORTANT]
> **v1 Scope Status:** This phase is **deferred to the v2 backlog**. In StudyLink v1, PDF text extraction, chunking, and Gemini vector embedding generation execute **synchronously** within the HTTP request handler cycle during file upload. Redis and Celery worker infrastructure setup is bypassed for v1.

---

## 1. Overview & v2 Backlog Reference

For v2, this module will establish an asynchronous task execution system using **Celery** with **Redis** as the message broker, routing tasks into isolated queues (`ingestion`, `notifications`, `default`).

### 1.1 Folder Structure (v2 Architecture Preview)
```text
backend/config/
├── __init__.py
├── celery.py                   # Celery application initialization (Deferred to v2)
├── settings.py                 # Celery broker configurations & queues definition (Deferred to v2)
backend/vault/
├── tasks.py                    # PDF ingestion worker tasks (Deferred to v2)
backend/market/
├── tasks.py                    # Notification trigger worker tasks (Deferred to v2)
```

---

## 2. v1 Synchronous Processing Strategy

In v1, the operations originally scoped for Celery are handled as follows:
- **PDF Extraction & Chunking:** Executed synchronously in `vault.services.PDFIngestionService` during `POST /api/v1/vault/` request execution.
- **Embedding Generation:** Executed synchronously via `GeminiClient.get_embedding()` and saved to `ResourceChunk` table before returning HTTP response.
- **Notification Triggers:** Saved directly to the `Notification` database model in Django view transaction hooks.
- **v1 Tradeoff:** Upload response latency scales directly with PDF document size. This is accepted as a v1 design constraint to eliminate Redis/Celery configuration friction.

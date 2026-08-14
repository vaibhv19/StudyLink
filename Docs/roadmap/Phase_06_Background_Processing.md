# Phase 06 — Background Processing

This phase establishes the asynchronous execution system for **StudyLink**. It configures **Celery** with **Redis** as the message broker, routes tasks into isolated queues (ingestion, notifications, default), and implements task retry policies and worker logging systems.

---

## 1. Module Design: `celery` App (Shared Core)

### 1.1 Folder Structure
```text
backend/config/
├── __init__.py
├── celery.py                   # Celery application initialization
├── settings.py                 # Celery broker configurations & queues definition
backend/vault/
├── tasks.py                    # Placeholder for ingestion and embedding tasks
backend/market/
├── tasks.py                    # Placeholder for notification dispatch triggers
```

### 1.2 Purpose
Enables asynchronous and out-of-process task execution for long-running CPU or I/O bound processes (like text extraction, embedding vectors, and dispatching alerts).

### 1.3 Dependencies
- `celery`
- `redis` (client library)
- Docker (to run local message broker container)

### 1.4 Inputs
- Task parameters passed during delay calls (`task.delay(*args, **kwargs)`).
- Environment configurations for broker URLs.

### 1.5 Outputs
- A running Celery worker listening to queues and processing background tasks.
- Task status changes logged in Redis backend.

### 1.6 Configuration Settings & Retry Policies

#### Routing Queues:
- **`ingestion`**: Dedicated for document reading, character splitting, and embedding calls.
- **`notifications`**: Dedicated for email triggers, in-app inbox logs updates, and audit listings.
- **`default`**: Fallback queue for general system maintenance.

#### Settings in `config/settings.py`:
- `CELERY_BROKER_URL`: Read from `.env` (default local Redis).
- `CELERY_RESULT_BACKEND`: Read from `.env` (default local Redis).
- `CELERY_TASK_SERIALIZER`: `'json'`
- `CELERY_RESULT_SERIALIZER`: `'json'`
- `CELERY_ACCEPT_CONTENT`: `['json']`
- `CELERY_TASK_ROUTES`: Map specific tasks to their target queues.
- `CELERY_TASK_DEFAULT_QUEUE`: `'default'`

#### Retry Policy Parameters:
- Max Retries: 3 attempts.
- Backoff delay: Exponential backoff with random jitter (`countdown = 2 ** self.request.retries + random.uniform(1, 5)`).
- Exceptions: Auto-retry on connection errors (`requests.exceptions.RequestException`, `redis.exceptions.ConnectionError`).

---

## 2. Implementation Tasks

### 2.1 Django Backend Layer (`backend/`)

#### Feature: Celery Application Bootstrap
Configure Celery and connect to the broker.

##### Task 06.01.01: Scaffold Celery Application class
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Phase 01 complete
- **Task Description:** Create `backend/config/celery.py`. Initialize the Celery app, auto-discover tasks in registered Django apps, and configure `__init__.py` in the config folder to load Celery.
- **Definition of Done:**
  - Running a local shell check validates that Celery instance is registered under the Django config namespace.

##### Task 06.01.02: Configure Broker, Result Backend & Task Routing
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Task 06.01.01
- **Task Description:** Configure broker connections and queue settings in `settings.py`. Route ingestion tasks to the `ingestion` queue and notification tasks to `notifications`.
- **Definition of Done:**
  - Task mapping route dict is present in the configuration.
  - Celery starts without throwing validation errors.

##### Task 06.01.03: Configure local docker-compose developer Redis container
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** None
- **Task Description:** Write a `docker-compose.yml` in the monorepo root. Expose port `6379` mapping to a Redis service instance for local message broker queues.
- **Definition of Done:**
  - Running `docker compose up -d` boots a Redis container.
  - Django and Celery can connect to `redis://127.0.0.1:6379/0` locally.

#### Feature: Task Skeleton Definitions & Error Recovery
Build the basic worker scripts.

##### Task 06.01.04: Implement Base Task Skeletons with logger configurations
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 06.01.02
- **Task Description:** Write basic task wrappers in `vault/tasks.py` (`process_pdf_document_task`) and `market/tasks.py` (`dispatch_marketplace_alerts_task`). Include logging to track task starts and completions.
- **Definition of Done:**
  - Skeletons are discovered by Celery.
  - Triggering tasks logs statements inside stdout.

##### Task 06.01.05: Implement Exponential Backoff Retry policy wrappers
- **Estimated Size:** S
- **Risk:** Medium
- **Prerequisites:** Task 06.01.04
- **Task Description:** Implement task retry wrappers using Celery's `@app.task(bind=True, max_retries=3)` decorator parameters. Add exponential backoffs and catch network and connection failures.
- **Definition of Done:**
  - Simulating a mock network exception inside a task triggers retries with expected delays before failing.

##### Task 06.01.06: Write Celery integration verification tests
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 06.01.05
- **Task Description:** Write unit tests using celery's `task_always_eager = True` settings parameter to evaluate task outputs synchronously during local unit testing.
- **Definition of Done:**
  - Unit tests run successfully and mock out active Celery workers.

# Phase 08 — Notification Engine

This phase covers building the asynchronous **Notification Engine**. It handles recording user alerts, routing notification triggers from marketplace and vault interactions, running Celery workers to write notifications to the database, and exposing the Notification Inbox APIs.

---

## 1. Module Design: `notifications` App

### 1.1 Folder Structure
```text
backend/notifications/
├── __init__.py
├── admin.py
├── apps.py
├── models.py                   # Notification model definition
├── serializers.py              # Notification serializers
├── tasks.py                    # Celery asynchronous dispatch tasks
├── urls.py                     # Notification API routes (/api/v1/notifications/*)
├── views.py                    # List view, Toggle read view, bulk read view
└── tests/
    ├── __init__.py
    ├── test_inbox.py           # Inbox retrieval tests
    └── test_triggers.py        # Verification of state machine integration triggers
```

### 1.2 Purpose
Provides in-app user notifications for important activities, such as receiving a request for a giveaway, having a request accepted, or updates to comments on followed study guides.

### 1.3 Dependencies
- `accounts` app (for recipient lookups)
- `vault` & `market` apps (source trigger events)

### 1.4 Inputs
- Signal events triggered by service-layer actions.
- Client PATCH updates to mark notifications as read.

### 1.5 Outputs
- Populated database notification records.
- Paginated user notification feeds.

### 1.6 Classes, Methods & Serialization Mappings

#### Model: `Notification`
- **Fields:**
  - `id`: `models.UUIDField` (default `uuid.uuid4`, primary key)
  - `recipient`: `models.ForeignKey` (`CustomUser`, on_delete=models.CASCADE, related_name="notifications")
  - `type`: `models.CharField` (choices: `NEW_REQUEST`, `REQUEST_ACCEPTED`, `REQUEST_CANCELED`, `ITEM_CLAIMED`, `UPVOTE_RECEIVED`, `NEW_COMMENT`)
  - `title`: `models.CharField` (max_length=255)
  - `message`: `models.TextField`
  - `is_read`: `models.BooleanField` (default `False`)
  - `created_at`: `models.DateTimeField` (auto_now_add=True)
- **Indexes:** `recipient`, `is_read`, `created_at`

#### Async Celery Task:
- `notifications.tasks.send_notification_task(recipient_id, notification_type, title, message)`: Reads configuration variables, writes records to PostgreSQL, and logs events.

---

## 2. Implementation Tasks

### 2.1 Django Backend Layer (`backend/`)

#### Feature: Models & Tasks Setup
Build the notification storage and task queues.

##### Task 08.01.01: Implement `Notification` Model
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Phase 03 complete
- **Task Description:** Define the `Notification` schema inside `notifications/models.py`. Set up model indexes for searching. Generate and run the migrations.
- **Definition of Done:**
  - Database schema contains the table `notifications_notification`.

##### Task 08.01.02: Create Notification Dispatch Celery Task
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Phase 06 complete, Task 08.01.01
- **Task Description:** Implement `send_notification_task` in `notifications/tasks.py`. The task writes a database row inside the notifications table and logs output status.
- **Definition of Done:**
  - Calling `send_notification_task.delay()` executes asynchronously and writes a record in the database.

#### Feature: Integration Triggers
Connect service actions to async alerts.

##### Task 08.01.03: Wire Marketplace state transitions to notification tasks
- **Estimated Size:** M
- **Risk:** Medium
- **Prerequisites:** Phase 05 complete, Task 08.01.02
- **Task Description:** Update marketplace service actions (`request_item`, `accept_request`, `cancel_request`, `complete_handoff`) to trigger the notification task:
  - When a request is submitted, notify the listing owner.
  - When a request is accepted, notify the selected recipient (with pickup details) and all other active requesters ("Item no longer available").
  - When a request is canceled, notify the owner or recipient.
- **Definition of Done:**
  - Accepting a request changes the listing state and queues background notification tasks for all involved users.

##### Task 08.01.04: Wire Upvote and Doubt Board comment posts to notification tasks
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Phase 04 complete, Task 08.01.02
- **Task Description:** In the vault comment and upvote services, trigger background notifications to notify resource uploaders when their guides get upvotes or comments.
- **Definition of Done:**
  - Posting comments creates the database comment rows and triggers background alerts for the uploader.

#### Feature: Notifications APIs
Build client-facing endpoints.

##### Task 08.01.05: Create Inbox List View
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 08.01.01
- **Task Description:** Create `GET /api/v1/notifications/` endpoint. Use standard pagination. Return user notifications, sorted by creation date.
- **Definition of Done:**
  - Querying the inbox endpoint returns the user's notification feed.

##### Task 08.01.06: Create Read Status Toggle API Endpoints
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 08.01.01
- **Task Description:** Create `PATCH /api/v1/notifications/{id}/read/` (toggles `is_read = True`) and `POST /api/v1/notifications/mark-all-read/` (sets `is_read = True` for all user notifications).
- **Definition of Done:**
  - Endpoint calls update notification read statuses in the database.

##### Task 08.01.07: Write Notification Service Integration Tests
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Task 08.01.06
- **Task Description:** Implement tests verifying alert routing rules, recipient filtering, database queries, and async task execution.
- **Definition of Done:**
  - All tests pass successfully.

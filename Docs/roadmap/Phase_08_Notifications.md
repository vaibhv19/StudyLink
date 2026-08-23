# Phase 08 — Notification Engine

This phase implements the in-app notification engine for **StudyLink**. It records alerts for key marketplace events (e.g., new requests, accepted handoffs) and vault interactions (e.g., resource upvotes, Doubt Board comments).

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
├── services.py                 # In-process notification dispatch services
├── urls.py                     # Notification inbox URLs
├── views.py                    # Views for listing and marking notifications as read
└── tests/
    ├── __init__.py
    ├── test_models.py          # Notification model tests
    └── test_triggers.py        # Trigger and read status tests
```

### 1.2 Purpose
Maintains user-specific notifications for marketplace status changes and vault activity.

---

## 2. Implementation Tasks

### 2.1 Django Backend Layer (`backend/`)

#### Feature: Notification Data Model & Scaffolding
Establish the database notification schema.

##### Task 08.01.01: Implement `Notification` Model & Migrations
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Phase 01 complete
- **Task Description:** Create `Notification` model with fields `recipient` (FK to User), `type` (e.g. `NEW_REQUEST`, `REQUEST_ACCEPTED`, `UPVOTE_RECEIVED`), `title`, `message`, `is_read`, and `created_at`. Generate and run migrations.
- **Definition of Done:**
  - Migrations run cleanly.

##### Task 08.01.02: Build In-Process Notification Dispatch Service
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 08.01.01
- **Task Description:** Write `notifications.services.send_notification(user_id, type, title, message)` helper function. Call this service in-process from marketplace and vault views upon event triggers.
- **Definition of Done:**
  - Event triggers create notification records directly in the database.

##### Task 08.01.03: Build Notification Inbox API Views
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 08.01.02
- **Task Description:** Create `GET /api/v1/notifications/` and `PATCH /api/v1/notifications/{id}/read/` endpoints.
- **Definition of Done:**
  - Authenticated users can retrieve their inbox and toggle `is_read` status.

# Phase 05 — Marketplace

This phase covers building the peer-to-peer physical giveaway platform (**Giveaway Marketplace**). It implements the listing schemas, interest request bindings, the `Available → Requested → Given Away` state machine, pessimistic database lock handlers, and the unified owner dashboard API.

---

## 1. Module Design: `market` App

### 1.1 Folder Structure
```text
backend/market/
├── __init__.py
├── admin.py
├── apps.py
├── models.py                   # Listing, ListingRequest, ListingStatusHistory
├── serializers.py              # Listing CRUD, Request detail, Dashboard responses
├── services.py                 # State Machine transitions, pessimistic locks
├── urls.py                     # Market endpoints (/api/v1/market/*)
├── views.py                    # Views for marketplace search, requests, state transitions, dashboard
└── tests/
    ├── __init__.py
    ├── test_marketplace.py     # Listing crud tests
    ├── test_state_machine.py   # State flow verification tests
    └── test_concurrency.py     # select_for_update locking race condition tests
```

### 1.2 Purpose
Provides a local giveaway coordination space utilizing strict state transitions and pessimistic locking to prevent double-accepting handoffs.

### 1.3 Dependencies
- `core` app (for optional Subject/Course course tags on items)
- `accounts` app (for verifying owners/requesters profiles)

### 1.4 Inputs
- Multipart listings (title, description, pickup area, condition, photo).
- PATCH state transition request actions (accept, cancel, complete).

### 1.5 Outputs
- Live listing database records.
- Immutable state change logs in `ListingStatusHistory`.
- Consolidated dashboard payloads.

### 1.6 Classes, Methods & Serialization Mappings

#### Model: `Listing`
- **Fields:**
  - `id`: `models.UUIDField` (default `uuid.uuid4`, primary key)
  - `owner`: `models.ForeignKey` (`CustomUser`, on_delete=models.CASCADE, related_name="listings")
  - `title`: `models.CharField` (max_length=200)
  - `status`: `models.CharField` (choices: `AVAILABLE`, `REQUESTED`, `GIVEN_AWAY`, default `AVAILABLE`, indexed)
  - `photo_url`: `models.ImageField` (saves to listing photos bucket in Supabase)
  - `pickup_area`: `models.TextField`
  - `condition`: `models.CharField` (choices: `New`, `Used - Good`, `Used - Fair`)
  - `is_active`: `models.BooleanField` (default `True`)
  - `subject`: `models.ForeignKey` (`Subject`, on_delete=models.SET_NULL, null=True, blank=True)
  - `course`: `models.ForeignKey` (`Course`, on_delete=models.SET_NULL, null=True, blank=True)

#### Model: `ListingRequest`
- **Fields:**
  - `id`: `models.UUIDField` (default `uuid.uuid4`, primary key)
  - `listing`: `models.ForeignKey` (`Listing`, on_delete=models.CASCADE, related_name="requests")
  - `requester`: `models.ForeignKey` (`CustomUser`, on_delete=models.CASCADE, related_name="sent_requests")
  - `status`: `models.CharField` (choices: `PENDING`, `ACCEPTED`, `REJECTED`, `WITHDRAWN`, default `PENDING`)
  - `created_at`: `models.DateTimeField` (auto_now_add=True)
- **Constraints:** Unique together (`listing`, `requester`) to prevent duplicate requests from the same user.

#### Model: `ListingStatusHistory`
- **Fields:**
  - `id`: `models.BigAutoField` (Primary Key)
  - `listing`: `models.ForeignKey` (`Listing`, on_delete=models.CASCADE, related_name="status_history")
  - `from_status`: `models.CharField` (max_length=20)
  - `to_status`: `models.CharField` (max_length=20)
  - `changed_by`: `models.ForeignKey` (`CustomUser`, on_delete=models.PROTECT)
  - `reason`: `models.TextField` (nullable)
  - `changed_at`: `models.DateTimeField` (auto_now_add=True)

---

## 2. Implementation Tasks

### 2.1 Django Backend Layer (`backend/`)

#### Feature: Schema & Models Setup
Build the marketplace data architecture.

##### Task 05.01.01: Implement `Listing`, `ListingRequest`, and `ListingStatusHistory` Models
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Phase 03 complete
- **Task Description:** Define the schemas for marketplace items in `market/models.py`. Set up DB constraints and indexes on statuses. Generate and apply database migrations.
- **Definition of Done:**
  - Database schema contains the tables `market_listing`, `market_listingrequest`, and `market_listingstatushistory`.

#### Feature: Marketplace Listings APIs
Build creation and discovery endpoints.

##### Task 05.01.02: Create Marketplace List & Detail Views
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Task 05.01.01
- **Task Description:** Implement `GET /api/v1/market/` and `GET /api/v1/market/{id}/`. List views must filter out items where `is_active = False` or `status = GIVEN_AWAY` (if older than 24 hours). Enable filtering by `pickup_area`, `subject` slugs, and `condition`.
- **Definition of Done:**
  - GET requests return paginated listing matches.
  - Detail endpoint includes nested pickup area details.

##### Task 05.01.03: Create Listing Creation View
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 05.01.01
- **Task Description:** Write a `POST /api/v1/market/` view. Parse incoming multipart layouts, stream upload photos to Supabase Storage, and record database rows with status initially set to `AVAILABLE`.
- **Definition of Done:**
  - Posting lists creates the model rows.
  - Photos are uploaded successfully to the S3 bucket.

#### Feature: State Machine Services
Build transition rules, locking, and audit logging.

##### Task 05.01.04: Implement Request Item view
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 05.01.01
- **Task Description:** Write `POST /api/v1/market/{id}/request/`. Check if listing is `AVAILABLE`. Ensure requester is not the listing owner. Create a new `ListingRequest` with status `PENDING`.
- **Definition of Done:**
  - Successful execution outputs a HTTP 201 response.
  - Submitting duplicate requests or requesting your own item returns a validation error.

##### Task 05.01.05: Implement `accept_request` State Transition Service with Pessimistic Locking
- **Estimated Size:** M
- **Risk:** High
- **Prerequisites:** Task 05.01.04
- **Task Description:** In `market/services.py`, implement `accept_request(owner, request_id)`. Wrap in a transaction:
  1. Retrieve the target `ListingRequest` record. Lock the parent `Listing` row using Django’s `.select_for_update()`.
  2. If the listing status is already `REQUESTED` or `GIVEN_AWAY`, raise a `ValidationError` yielding an API HTTP 409 Conflict.
  3. Otherwise, set the listing status to `REQUESTED`. Update the selected request status to `ACCEPTED` and all other pending requests to `REJECTED`.
  4. Write a record to `ListingStatusHistory`.
- **Definition of Done:**
  - Accepts a request and updates listing states atomically.
  - Simultaneous race attempts to accept different users trigger a database lock, resolving one while returning a HTTP 409 error to the second attempt.

##### Task 05.01.06: Implement `cancel_request` Transition Service
- **Estimated Size:** M
- **Risk:** Medium
- **Prerequisites:** Task 05.01.05
- **Task Description:** Implement `cancel_request(user, request_id)` service. Ensure user is the owner or the accepted recipient. Set the request status to `REJECTED` (if canceled by owner) or `WITHDRAWN` (if canceled by requester). Revert the parent listing status back to `AVAILABLE`. Write audit logs.
- **Definition of Done:**
  - Transition reverts listing status back to `AVAILABLE`.
  - Item is returned to search listings index pages immediately.

##### Task 05.01.07: Implement `complete_handoff` Transition Service
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 05.01.05
- **Task Description:** Implement `complete_handoff(owner, listing_id)` service. Ensure user is owner. Set listing status to terminal `GIVEN_AWAY` state. Write audit logs.
- **Definition of Done:**
  - Transitions listing to `GIVEN_AWAY`.

##### Task 05.01.08: Create State Transition and History API Endpoints
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 05.01.05, Task 05.01.06, Task 05.01.07
- **Task Description:** Register endpoints `/api/v1/market/requests/{id}/accept/` (POST/PATCH), `/api/v1/market/requests/{id}/cancel/` (POST/PATCH), and `/api/v1/market/{id}/complete/` (POST/PATCH) mapping to the services. Create `/api/v1/market/{id}/history/` to fetch history logs.
- **Definition of Done:**
  - APIs trigger backend state transitions.

#### Feature: User Dashboard API
Develop dashboard integration view.

##### Task 05.01.09: Implement Unified Owner Dashboard API View
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Task 05.01.01
- **Task Description:** Write `GET /api/v1/dashboard/owner/`. Retrieve and structure user's active listings, their pending requests, and requests sent by the user to other listings.
- **Definition of Done:**
  - Single API response contains user listings, nested pending requests, and active requests.

##### Task 05.01.10: Write Marketplace Test Suites
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Task 05.01.09
- **Task Description:** Write tests verifying state machine transitions, concurrent locking checks, permissions logic, and history tracking.
- **Definition of Done:**
  - pytest test suites run and pass successfully.

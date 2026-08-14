# Phase 04 — Resource Vault

This phase covers building the digital file library (**Resource Vault**). It handles PDF metadata registration, django-storages S3 integrations with Supabase Storage, upvote/rating triggers, and the threaded discussion boards (Doubt Boards) localized to each resource.

---

## 1. Module Design: `vault` App

### 1.1 Folder Structure
```text
backend/vault/
├── __init__.py
├── admin.py
├── apps.py
├── models.py                   # Resource, ResourceUpvote, DoubtBoardComment
├── serializers.py              # ResourceUpload, ResourceDetail, CommentSerializers
├── services.py                 # File upload utilities, Upvote handler, Comment moderator
├── urls.py                     # Vault endpoints (/api/v1/vault/*)
├── views.py                    # Views for Vault CRUD, rating toggle, and comment threads
└── tests/
    ├── __init__.py
    ├── test_vault_crud.py      # Resource metadata and retrieval tests
    ├── test_upvotes.py         # Concurrency rating tests
    └── test_comments.py        # Nested board thread tests
```

### 1.2 Purpose
Provides a digital note repository allowing students to upload documents, filter notes by subjects/courses, and engage in threaded Q&A discussions.

### 1.3 Dependencies
- `core` app (for academic subjects/courses)
- `accounts` app (for user uploader validation)
- `django-storages` (S3 backend configured to target Supabase Storage buckets)

### 1.4 Inputs
- Multipart-form payloads (PDF documents, subject ID, course ID, title).
- JSON comment text strings.

### 1.5 Outputs
- Metadata rows in database.
- Streamed PDF storage items in Supabase.
- Localized comment hierarchy data lists.

### 1.6 Classes, Methods & Serialization Mappings

#### Model: `Resource`
- **Fields:**
  - `id`: `models.UUIDField` (default `uuid.uuid4`, primary key)
  - `uploader`: `models.ForeignKey` (`CustomUser`, on_delete=models.CASCADE, related_name="uploaded_resources")
  - `title`: `models.CharField` (max_length=255)
  - `file_path`: `models.FileField` (uploads to standard folder paths in storage)
  - `subject`: `models.ForeignKey` (`Subject`, on_delete=models.PROTECT)
  - `course`: `models.ForeignKey` (`Course`, on_delete=models.PROTECT)
  - `status`: `models.CharField` (choices: `PROCESSING`, `READY`, `FAILED`, `UNSEARCHABLE`, default `PROCESSING`)
  - `is_active`: `models.BooleanField` (default `True`)
  - `upvote_count`: `models.IntegerField` (default 0, denormalized)
- **Indexes:** `subject`, `course`, `is_active`

#### Model: `ResourceUpvote`
- **Fields:**
  - `id`: `models.AutoField` (Primary Key)
  - `resource`: `models.ForeignKey` (`Resource`, on_delete=models.CASCADE, related_name="upvotes")
  - `user`: `models.ForeignKey` (`CustomUser`, on_delete=models.CASCADE)
- **Constraints:** Unique together (`resource`, `user`)

#### Model: `DoubtBoardComment`
- **Fields:**
  - `id`: `models.AutoField` (Primary Key)
  - `resource`: `models.ForeignKey` (`Resource`, on_delete=models.CASCADE, related_name="comments")
  - `user`: `models.ForeignKey` (`CustomUser`, on_delete=models.CASCADE)
  - `parent`: `models.ForeignKey` ("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
  - `content`: `models.TextField`
  - `is_solved`: `models.BooleanField` (default `False`)
  - `created_at`: `models.DateTimeField` (auto_now_add=True)

---

## 2. Implementation Tasks

### 2.1 Django Backend Layer (`backend/`)

#### Feature: Resource Storage & Schema Setup
Set up metadata structures and configure AWS S3 SDK wrappers targeting Supabase buckets.

##### Task 04.01.01: Implement `Resource` & `ResourceUpvote` Models
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Phase 03 complete
- **Task Description:** Define the `Resource` and `ResourceUpvote` models in `vault/models.py`. Set up model indexes for searching. Generate and run the migrations.
- **Definition of Done:**
  - Database schema contains the tables `vault_resource` and `vault_resourceupvote`.

##### Task 04.01.02: Configure Supabase Storage / S3 backend settings
- **Estimated Size:** M
- **Risk:** Medium
- **Prerequisites:** Task 04.01.01
- **Task Description:** In `settings.py`, configure `django-storages` AWS settings (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_ENDPOINT_URL`, `AWS_DEFAULT_ACL = None`) pointing to Supabase S3-compatible endpoints. Configure a custom file storage class to isolate files under `/resources/` bucket keys.
- **Definition of Done:**
  - Initial tests checking file saves save successfully to Supabase rather than storing on the local disk.

#### Feature: Vault Discovery & Upload APIs
Develop APIs allowing students to download and find uploaded guides.

##### Task 04.01.03: Create Resource Upload API View & Serializer
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Task 04.01.02
- **Task Description:** Write a `POST /api/v1/vault/` endpoint. Use DRF views supporting multipart parsing to read uploaded files. On write, save the resource metadata in the database with status set to `PROCESSING`.
- **Definition of Done:**
  - Sending a POST request creates the database row and uploads the raw PDF to the cloud storage bucket.
  - Returns a serialized metadata object with status `PROCESSING`.

##### Task 04.01.04: Create Resource Query Lists Views with filtering logic
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Task 04.01.03
- **Task Description:** Create `GET /api/v1/vault/` and `GET /api/v1/vault/{id}/` endpoints. Implement DjangoFilterBackend to allow search queries filtering by `subject` slugs, `course` codes, and text query matching on the `title` string.
- **Definition of Done:**
  - List endpoint returns paginated resources where `is_active = True`.
  - Filter queries (e.g. `?course=CS101`) correctly isolate matching items.

##### Task 04.01.05: Create Upvote Toggle Action View
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 04.01.01
- **Task Description:** Implement POST `/api/v1/vault/{id}/rate/` endpoint. Check if the active user has already upvoted this resource using `ResourceUpvote` lookups. If present, delete the row and decrement `upvote_count` atomically using `F('upvote_count') - 1`. Otherwise, insert the record and increment the count.
- **Definition of Done:**
  - POST calls toggle the upvote state atomically.
  - The API response returns the updated upvote counts and user status.

#### Feature: Doubt Board Q&A
Develop discussion boards.

##### Task 04.01.06: Implement `DoubtBoardComment` & Nested Comments API views
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Task 04.01.01
- **Task Description:** Write models and serializers for `DoubtBoardComment`. Create `GET /api/v1/vault/{id}/comments/` (returns comment trees) and `POST /api/v1/vault/{id}/comments/` (posts comments, supports parent ID references for replies). Create a `PATCH` toggle enabling posters or resource uploaders to check comments as `is_solved = True`.
- **Definition of Done:**
  - Comments can be posted and retrieved in organized nested trees.
  - Toggling solutions updates flags correctly.

##### Task 04.01.07: Write Vault API Test Suites
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Task 04.01.06
- **Task Description:** Implement unit tests verifying file saving overrides, filter parameters, upvote database locking, and solved flag permissions rules.
- **Definition of Done:**
  - pytest executions pass cleanly.

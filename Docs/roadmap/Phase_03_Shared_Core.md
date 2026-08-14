# Phase 03 — Shared Core Infrastructure

This phase establishes the shared foundation for **StudyLink**. It implements the `core` app, containing academic subject/course tag databases, standardized API pagination helpers, global HTTP exception formats, and custom validations.

---

## 1. Module Design: `core` App

### 1.1 Folder Structure
```text
backend/core/
├── __init__.py
├── admin.py
├── apps.py
├── exceptions.py               # Global exception formatter
├── models.py                   # Subject and Course models
├── serializers.py              # Serializers for Subject & Course lists
├── pagination.py               # API Pagination configurations
├── urls.py                     # Core lists endpoints (/api/v1/core/*)
├── views.py                    # List endpoints for tags
└── tests/
    ├── __init__.py
    ├── test_tags.py            # Tag lists and constraints tests
    └── test_exceptions.py      # Exception handler tests
```

### 1.2 Purpose
Provides centralized academic tag metadata (Subjects & Courses) and standardizes API response schemas, error formatting, and pagination behavior across the entire system.

### 1.3 Dependencies
- `djangorestframework`

### 1.4 Inputs
- Queries filtering tags.
- Internal raw exceptions and validation failures.

### 1.5 Outputs
- Structured list of valid academic subjects/courses.
- Uniform JSON error payloads matching the API contract.

### 1.6 Classes, Methods & Serialization Mappings

#### Model: `Subject`
- **Fields:**
  - `id`: `models.AutoField` (Primary Key)
  - `name`: `models.CharField` (max_length=100, unique, e.g., "Computer Science")
  - `slug`: `models.SlugField` (unique, e.g., "computer-science")

#### Model: `Course`
- **Fields:**
  - `id`: `models.AutoField` (Primary Key)
  - `subject`: `models.ForeignKey` (linked to `Subject`, on_delete=CASCADE)
  - `name`: `models.CharField` (max_length=150, e.g., "Intro to Programming")
  - `code`: `models.CharField` (max_length=20, unique, indexed, e.g., "CS101")

#### Exception Handling:
- `core.exceptions.custom_exception_handler(exc, context)`: Intercepts DRF exceptions and reformats them to:
  ```json
  {
    "code": "error_code_string",
    "message": "Human readable detail",
    "fields": { "field_name": ["Specific validation error"] }
  }
  ```

#### Pagination:
- `core.pagination.StandardResultsSetPagination`: Inherits from `PageNumberPagination`. Sets `page_size = 20`, `max_page_size = 100`, and maps keys: `results`, `count`, `next`, `previous`.

---

## 2. Implementation Tasks

### 2.1 Django Backend Layer (`backend/`)

#### Feature: Shared Tag Models & DB Seeding
Initialize the static catalog of subjects and courses.

##### Task 03.01.01: Implement `Subject` and `Course` Models
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Phase 01 complete
- **Task Description:** Write database models for `Subject` and `Course` inside `core/models.py`. Generate database migration files. Register these models in `core/admin.py` for supervisor editing.
- **Definition of Done:**
  - Database schema contains `core_subject` and `core_course` tables.
  - Adding a new course through the Django admin panel works correctly.

##### Task 03.01.02: Create DB Seed Script for Academic Tags
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 03.01.01
- **Task Description:** Write a custom Django management command `seed_tags` under `core/management/commands/seed_tags.py`. The command must populate the database with common college subjects (e.g., Computer Science, Mathematics, Physics) and courses (e.g., CS101, MATH201, PHYS102).
- **Definition of Done:**
  - Running `python manage.py seed_tags` runs without error.
  - Repeating the seed script executes safely without inserting duplicate rows.

##### Task 03.01.03: Create Tags List Endpoints
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 03.01.01
- **Task Description:** Write endpoints `/api/v1/core/subjects/` and `/api/v1/core/courses/` allowing public GET requests. The list view should support query filters (e.g., `/api/v1/core/courses/?subject=computer-science`).
- **Definition of Done:**
  - Querying `/api/v1/core/courses/` returns a JSON list of courses nested with subject references.

#### Feature: Global API Formatter Configuration
Configure standardized error responses and pagination layouts.

##### Task 03.01.04: Implement Custom Exception Handler Middleware
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Phase 01 complete
- **Task Description:** Implement `custom_exception_handler` in `core/exceptions.py`. Intercept all REST validation errors (like serializer validation checks), unauthorized triggers, permissions failures, and database connection losses. Map their formats to compile custom code strings and nested fields error summaries. Register the handler in `settings.py` via `EXCEPTION_HANDLER`.
- **Definition of Done:**
  - A client validation error returns HTTP 400 with a dictionary containing `code: "validation_error"`, a human-readable `message`, and specific validation error arrays mapped under the `fields` key.
  - Non-DRF unhandled Python runtime exceptions are gracefully formatted as HTTP 500 errors.

##### Task 03.01.05: Implement Custom Pagination Helper class
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Phase 01 complete
- **Task Description:** Define `StandardResultsSetPagination` inside `core/pagination.py`. Use it as the default pagination class in the `REST_FRAMEWORK` configuration dictionary in `settings.py`.
- **Definition of Done:**
  - API responses for lists include page metadata: total count, next page link, previous page link, and data results array.

##### Task 03.01.06: Write Core Infrastructure Tests
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 03.01.04, Task 03.01.05
- **Task Description:** Write test suites in `core/tests/` evaluating exception format conversions and validating subject/course filter queries.
- **Definition of Done:**
  - Running `python manage.py test core` runs with 100% success rate.

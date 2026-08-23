# Learning Doc 05: DRF Architecture: Serializers, ViewSets & Permissions

> **Topic**: Production API Patterns in Django REST Framework: Data Validation, Custom Permissions, Pagination, and Standardized Error Handling.

---

## 1. Problem / Concept

Building clean, maintainable web APIs requires separating HTTP transport logic from business rules and data formatting. Unstructured API controllers lead to duplicated code, inconsistent error payloads, missing validation checks, and security vulnerabilities.

Django REST Framework (DRF) provides architectural building blocks to enforce separation of concerns:
- **Serializers**: Handle two-way translation between complex Django ORM model instances and Python primitives / JSON, including payload validation.
- **Views & Generic Views**: Manage HTTP request methods (`GET`, `POST`, `PATCH`, `DELETE`) and delegate actions.
- **Permissions**: Control access based on authentication state and object ownership.
- **Exception Handlers**: Intercept unhandled API exceptions to return consistent error structures.

---

## 2. How It Works Generally

- **Read vs. Write Serializers**: Creation requests often accept raw inputs (e.g. uploaded file, foreign key IDs) whereas read responses return enriched nested representations (e.g. file URL, nested user details).
- **Pagination**: Slices database querysets into uniform pages (e.g. 10 or 20 items) with `count`, `next`, `previous`, and `results` keys.
- **Custom Exception Handling**: Converts native Python/Django exceptions (such as `ValidationError`, `PermissionDenied`, or custom `ConflictError`) into standardized JSON error envelopes.

---

## 3. How StudyLink Specifically Uses It

Across `backend/core/`, `backend/vault/`, and `backend/market/`:

1. **Dual Serializers**:  
   In `vault/views.py`, `ResourceListCreateView` dynamically selects `ResourceUploadSerializer` for `POST` requests (validates PDF file extension and subject/course relationships) and `ResourceSerializer` for `GET` requests (enriches output with absolute file URLs, uploader profile details, and `has_upvoted` status).
2. **Standardized Pagination (`StandardResultsSetPagination`)**:  
   Configured in `core/pagination.py` as default `DEFAULT_PAGINATION_CLASS`, returning 20 items per page with optional `page_size` overrides.
3. **Centralized Exception Handler (`custom_exception_handler`)**:  
   In `core/exceptions.py`, DRF's exception handler is wrapped to format all errors into a clean, predictable contract:
   ```json
   {
     "code": "permission_denied",
     "message": "You do not have permission to perform this action.",
     "details": {}
   }
   ```
4. **Object Permissions**:  
   Views enforce granular security (e.g. `UpvoteToggleView` checks `resource.uploader != request.user` to prevent self-upvoting, returning `HTTP_403_FORBIDDEN`).

---

## 4. Key Files & Code References

- [backend/core/exceptions.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/core/exceptions.py#L1-L60) — `custom_exception_handler` function formatting standardized JSON error payloads.
- [backend/core/pagination.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/core/pagination.py#L1-L10) — `StandardResultsSetPagination` definition.
- [backend/vault/serializers.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/vault/serializers.py#L11-L69) — `ResourceSerializer` vs `ResourceUploadSerializer`.
- [backend/vault/views.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/vault/views.py#L54-L106) — `UpvoteToggleView` custom permission and upvote counter logic.

---

## 5. Interview Deep-Dive Takeaways

> [!TIP]
> **What to highlight in an interview:**
> 1. **Why Separate Read and Write Serializers?**  
>    "Using dedicated upload/create serializers keeps validation logic clean and prevents over-posting attacks, while read serializers return rich nested objects without requiring extra client API calls."
> 2. **Consistent API Error Contracts**:  
>    "Overriding DRF's `EXCEPTION_HANDLER` guarantees that frontend client code receives predictable `{ code, message, details }` payloads across all endpoints, whether the failure stems from database constraints, permission checks, or business logic errors."

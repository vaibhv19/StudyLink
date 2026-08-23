# API_Specification.md — StudyLink

This document defines the REST API contract between the React frontend and the Django backend. The API is versioned and follows standard RESTful principles, using HTTP Bearer tokens (JWT) for authenticated sessions.

---

## 1. Global Conventions

- **Base URL:** `https://<cloud-run-domain>.run.app/api/v1`
- **Content Type:** `application/json` (unless `multipart/form-data` for file/image uploads)
- **Authentication:** `Authorization: Bearer <access_token>`
- **Error Format:**
  ```json
  {
    "code": "error_code_string",
    "message": "Human readable detail",
    "fields": { "field_name": ["Specific validation error"] }
  }
  ```

---

## 2. Authentication (`/auth`)

| Endpoint | Method | Auth | Description |
| :--- | :--- | :--- | :--- |
| `/register/` | `POST` | Public | Creates new user account with email, password, and full name. Returns JWT access token. |
| `/login/` | `POST` | Public | Authenticates credentials and returns Access token + sets Refresh token HttpOnly cookie. |
| `/token/refresh/` | `POST` | Public | Rotates the access token using a valid refresh token cookie. |

*Note: OAuth endpoints (`/social/google/`, `/social/github/`) are deferred to the v2 backlog.*

---

## 3. Resource Vault (`/vault`)

| Endpoint | Method | Auth | Description |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | Public | List resources with filters (`subject`, `course`, `search`). |
| `/` | `POST` | Private | Upload PDF resource. (Multipart: `file`, `title`, `subject`, `course`). Synchronously chunks text and generates vector embeddings upon upload. |
| `/{id}/` | `GET` | Public | Get resource metadata and Supabase file URL. |
| `/{id}/upvote/` | `POST` | Private | Toggle upvote/rating on a resource. |
| `/{id}/comments/` | `GET` | Public | List Doubt Board discussion for the resource. |
| `/{id}/comments/` | `POST` | Private | Post a new comment/question to the Doubt Board. |

---

## 4. Scoped AI Chat (`/chat`)

Executing queries against a single document context.

**Endpoint:** `POST /chat/query/`  
**Auth:** Private

**Request Body:**
```json
{
  "resource_id": "UUID",
  "query": "How is the O(n) complexity explained in these notes?"
}
```

**Response Body (200 OK):**
```json
{
  "answer": "The notes explain O(n) as...",
  "sources": [
    {
      "page_number": 4,
      "excerpt": "...linear growth relative to input size...",
      "similarity_score": 0.89
    }
  ]
}
```

---

## 5. Giveaway Marketplace (`/market`)

Managing physical items and the `Available → Requested → Given Away` state machine.

| Endpoint | Method | Auth | Description |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | Public | List giveaway items with filters (`pickup_area`, `subject`, `condition`). |
| `/` | `POST` | Private | Create a listing. (Multipart: `photo`, `title`, `description`, `pickup_area`). |
| `/{id}/` | `GET` | Public | Detail view of a listing + pickup area info. |
| `/{id}/request/` | `POST` | Private | Interested user sends a request to the owner. |
| `/{id}/status/` | `PATCH` | Private | Owner updates status (e.g., to `Given Away` or back to `Available`). |
| `/{id}/history/` | `GET` | Private | Returns chronological log of status changes and request activity. |

---

## 6. Owner Dashboard (`/dashboard`)

This endpoint is designed to power the unified management view for the active user.

**Endpoint:** `GET /dashboard/owner/`  
**Auth:** Private

**Response Body (200 OK):**
```json
{
  "my_listings": [
    {
      "id": "UUID",
      "title": "Calculus Early Transcendentals",
      "status": "REQUESTED",
      "request_count": 3,
      "recent_requests": [
        { "id": "req_1", "user_name": "Alice", "created_at": "2023-10-01T..." }
      ]
    }
  ],
  "my_active_requests": [
    { "listing_id": "UUID", "listing_title": "Lab Goggles", "status": "PENDING" }
  ]
}
```

---

## 7. Status Codes Summary

- `200 OK`: Request successful.
- `201 Created`: Resource (Upload/Listing/Request) successfully created.
- `400 Bad Request`: Validation error (e.g., invalid subject tag or weak password).
- `401 Unauthorized`: Missing or expired JWT access token.
- `403 Forbidden`: Attempting to update a listing or upvote own resource.
- `500 Internal Server Error`: Server-side failure (e.g., Gemini API timeout or Supabase connection loss).
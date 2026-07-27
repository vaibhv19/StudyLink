# DB_Schema.md — StudyLink Database Design

This document defines the relational schema and vector storage architecture for **StudyLink**. The database is hosted on **Supabase Postgres** and utilizes the `pgvector` extension for semantic retrieval.

---

## 1. Entity Relationship Diagram (ASCII)

```text
  [users] 1 ------ * [resources] 1 ------ * [resource_chunks] (vector)
     |                 |
     |                 * [doubt_board_comments]
     |
     +--------- 1 ------ * [listings] 1 ------ * [listing_status_history]
     |                       |
     |                       1
     |                       |
     +--------- 1 ------ * [requests]
     |
     * [notifications]
```

---

## 2. Table Dictionary

1.  **`users`**: Core identity table supporting JWT credentials and multiple OAuth providers.
2.  **`resources`**: Metadata for digital vault items (PDFs/Notes) stored in Supabase Storage.
3.  **`resource_chunks`**: Segmented text passages with high-dimensional embeddings for RAG.
4.  **`doubt_board_comments`**: Threaded discussions localized to specific resources.
5.  **`listings`**: Physical marketplace items with state-machine controlled status.
6.  **`requests`**: Join table representing interest from a student in a marketplace listing.
7.  **`listing_status_history`**: Immutable audit trail for all marketplace state transitions.
8.  **`notifications`**: User-specific alerts triggered by marketplace or vault activity.

---

## 3. Table Definitions

### 3.1 `users`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK | Primary identifier. |
| `email` | `VARCHAR(255)` | UNIQUE, INDEX | Primary contact and login key. |
| `password` | `VARCHAR(255)` | NULLABLE | Hash for email/password auth; nullable for OAuth-only accounts. |
| `provider` | `VARCHAR(20)` | | Primary auth provider for the account (`local`, `google`, `github`). |
| `linked_google` | `BOOLEAN` | DEFAULT FALSE | Whether the account is linked to Google OAuth. |
| `linked_github` | `BOOLEAN` | DEFAULT FALSE | Whether the account is linked to GitHub OAuth. |
| `full_name` | `VARCHAR(100)` | | User's display name. |
| `avatar_url` | `TEXT` | | Link to profile photo. |

### 3.2 `resources`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK | Primary identifier. |
| `uploader_id` | `UUID` | FK (users) | User who contributed the material. |
| `title` | `VARCHAR(255)` | | Resource name. |
| `file_path` | `TEXT` | | Reference key in Supabase Storage. |
| `subject_tag` | `VARCHAR(50)` | INDEX | Subject filter (e.g., "CS101"). |
| `course_code` | `VARCHAR(20)` | INDEX | Specific course identifier. |
| `status` | `VARCHAR(20)` | | Resource lifecycle: `PROCESSING`, `READY`, `FAILED`, `UNSEARCHABLE`. |
| `is_active` | `BOOLEAN` | DEFAULT TRUE | Soft-delete flag for resource archival. |
| `upvote_count` | `INTEGER` | DEFAULT 0 | Denormalized count for performance. |

### 3.3 `resource_chunks`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK | Primary identifier. |
| `resource_id` | `UUID` | FK (resources) | Parent document reference. |
| `content` | `TEXT` | | Raw text segment. |
| `page_number` | `INTEGER` | | Source page for citation. |
| `embedding` | `VECTOR(768)` | INDEX (HNSW) | Gemini `text-embedding-004` vector. |

### 3.4 `listings`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK | Primary identifier. |
| `owner_id` | `UUID` | FK (users) | Seller/Giver of the item. |
| `title` | `VARCHAR(200)` | | Item name. |
| `status` | `VARCHAR(20)` | INDEX | `AVAILABLE`, `REQUESTED`, `GIVEN_AWAY`. |
| `photo_url` | `TEXT` | | Supabase Storage image reference. |
| `pickup_area` | `TEXT` | | General area description for handoff. |
| `condition` | `VARCHAR(50)` | | `New`, `Used - Good`, `Used - Fair`. |
| `is_active` | `BOOLEAN` | DEFAULT TRUE | Soft-delete flag for listing archival. |

### 3.5 `requests`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK | Primary identifier. |
| `listing_id` | `UUID` | FK (listings) | Targeted item. |
| `requester_id` | `UUID` | FK (users) | Student interested in the item. |
| `status` | `VARCHAR(20)` | | `PENDING`, `ACCEPTED`, `REJECTED`, `WITHDRAWN`. |
| `created_at` | `TIMESTAMP` | | Used to sort owner dashboard requests. |

### 3.6 `listing_status_history`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `BIGINT` | PK | Sequential log ID. |
| `listing_id` | `UUID` | FK (listings) | Parent listing reference. |
| `from_status` | `VARCHAR(20)` | | Previous state. |
| `to_status` | `VARCHAR(20)` | | New state. |
| `changed_at` | `TIMESTAMP` | | Audit timestamp. |

### 3.7 `notifications`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK | Primary identifier. |
| `recipient_id` | `UUID` | FK (users) | User receiving the notification. |
| `type` | `VARCHAR(50)` | | Event type such as `NEW_MARKETPLACE_REQUEST` or `RESOURCE_UPVOTE`. |
| `title` | `VARCHAR(255)` | | Short notification title. |
| `message` | `TEXT` | | Human-readable notification body. |
| `is_read` | `BOOLEAN` | DEFAULT FALSE | Read/unread state. |
| `created_at` | `TIMESTAMP` | | Notification timestamp. |

---

## 4. Indexing Rationale

1.  **Vector Search (`resource_chunks.embedding`)**:
    - **Type**: `HNSW` (Hierarchical Navigable Small World).
    - **Rationale**: Provides high-speed approximate nearest neighbor search. Crucial for the Chat-with-notes feature where we filter by `resource_id` and then perform vector similarity.
2.  **Marketplace Filtering (`listings.status`, `listings.subject_tag`)**:
    - **Type**: `B-Tree`.
    - **Rationale**: Users frequently filter the marketplace for "Available" items only. Indexing these columns prevents full table scans on the browse screen.
3.  **Vault Discovery (`resources.subject_tag`, `resources.course_code`)**:
    - **Type**: `B-Tree`.
    - **Rationale**: Academic search is almost always centered on these two identifiers.
4.  **Auth Speed (`users.email`)**:
    - **Type**: `B-Tree / Unique`.
    - **Rationale**: Essential for rapid JWT token issuance and OAuth identity mapping during login.

---

## 5. Data Integrity Rules

- **Soft Deletion**: `resources` and `listings` use `is_active` rather than hard deletion to preserve the `listing_status_history` and `resource_chunks` for analytics.
- **State Constraint**: `requests.status` cannot be set to `ACCEPTED` if the parent `listings.status` is already `REQUESTED` by another user (enforced via database transaction in the service layer).
- **Notification Handling**: `notifications` are generated asynchronously via Celery tasks following marketplace and resource events, while preserving `resource_chunks` for existing RAG content.
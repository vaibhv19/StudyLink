# StudyLink Backend

> Django 5.1 REST API backend providing authentication, Resource Vault document processing, pgvector RAG vector search, marketplace state machine management, and notifications.

---

## 🏗️ Architecture & App Structure

The backend follows a modular Django application layout:

```
backend/
├── accounts/         # Custom User model, SimpleJWT authentication & OAuth services
├── vault/            # PDF resource storage, text chunk extraction & doubt board comments
├── market/           # Marketplace listings, request state machine & pessimistic locking
├── rag/              # Gemini API client, embedding generation & pgvector similarity search
├── notifications/    # User notification models & synchronous event handlers
├── core/             # Core models (Subject, Course), custom exception handlers & pagination
└── config/           # Django settings, root URLs, WSGI/ASGI configurations
```

---

## 🔑 Required Environment Variables

Configure these in `backend/.env` (see `backend/.env.example`):

| Variable | Description | Example / Diagnostic Note |
|---|---|---|
| `SECRET_KEY` | Django cryptographic signing key | Minimum 32-character string |
| `DEBUG` | Enable debug mode | `True` for dev, `False` for prod |
| `ALLOWED_HOSTS` | Allowed HTTP host headers | `localhost,127.0.0.1` |
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql://user:pass@host:6543/postgres` (Falls back to SQLite if omitted) |
| `USE_S3` | Toggle Supabase S3 / local storage | `True` (uses S3 storage backend), `False` (uses local media folder) |
| `AWS_ACCESS_KEY_ID` | S3 Access Key ID for Supabase | Hex key from Supabase Storage S3 settings |
| `AWS_SECRET_ACCESS_KEY` | S3 Secret Access Key | Hex secret from Supabase Storage S3 settings |
| `AWS_STORAGE_BUCKET_NAME` | Supabase S3 bucket name | `studylink-S3` |
| `AWS_S3_ENDPOINT_URL` | Supabase S3 S3-compatible URL | `https://<project-ref>.storage.supabase.co/storage/v1/s3` |
| `GEMINI_API_KEY` | Google Gemini API key | Required for RAG embeddings (`text-embedding-004`) & Q&A (`gemini-1.5-flash`) |
| `CORS_ALLOWED_ORIGINS` | Permitted cross-origin origins | `http://localhost:5173` |

---

## ⚡ Database Migrations & Commands

```bash
# Run database migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Run backend unit tests
python manage.py test

# Run Django development server
python manage.py runserver 8000
```

---

## 📡 API Surface at a Glance

### Authentication (`/api/v1/accounts/`)
- `POST /api/v1/accounts/register/` — Register local user account.
- `POST /api/v1/accounts/login/` — Authenticate and retrieve JWT access & refresh tokens.
- `POST /api/v1/accounts/token/refresh/` — Obtain new access token via refresh token.
- `GET /api/v1/accounts/profile/` — Fetch authenticated user profile.
- `POST /api/v1/accounts/oauth/google/` — Authenticate or link Google OAuth account.

### Resource Vault (`/api/v1/vault/`)
- `GET /api/v1/vault/` — List active study resources with subject/course/search filtering.
- `POST /api/v1/vault/` — Upload a PDF resource (triggers chunk extraction & embedding).
- `GET /api/v1/vault/{id}/` — Retrieve resource details.
- `POST /api/v1/vault/{id}/rate/` — Toggle upvote on a resource.
- `GET /api/v1/vault/{id}/comments/` — Fetch doubt board comment tree.
- `POST /api/v1/vault/{id}/comments/` — Post a comment or reply on a resource.

### RAG Document Assistant (`/api/v1/rag/`)
- `POST /api/v1/rag/chat/` — Query Gemini RAG engine for grounded Q&A with page citations.

### Marketplace (`/api/v1/market/`)
- `GET /api/v1/market/` — List active marketplace items.
- `POST /api/v1/market/` — Post a new study material listing.
- `GET /api/v1/market/{id}/` — Retrieve listing details.
- `POST /api/v1/market/{id}/request/` — Request an available listing.
- `POST /api/v1/market/requests/{id}/accept/` — Accept request (transitions listing to `REQUESTED`, locks row).
- `POST /api/v1/market/requests/{id}/cancel/` — Cancel or withdraw request (reverts listing to `AVAILABLE`).
- `POST /api/v1/market/{id}/complete/` — Complete handoff (transitions listing to `GIVEN_AWAY`).
- `GET /api/v1/market/dashboard/` — Retrieve owner dashboard & active sent requests.

### Notifications (`/api/v1/notifications/`)
- `GET /api/v1/notifications/` — List user notifications.
- `PATCH /api/v1/notifications/{id}/` — Mark notification as read.

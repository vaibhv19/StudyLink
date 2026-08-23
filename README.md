# StudyLink

> **Empowering Academic Collaboration & Resource Sharing**  
> StudyLink is a full-stack academic platform featuring a **Resource Vault** powered by RAG (Retrieval-Augmented Generation) document Q&A and an **Peer-to-Peer Marketplace** for textbook and study material handoffs.

---

## 🌟 The Two-Module Pitch

StudyLink solves two core challenges for university students:

1. **The Resource Vault (Smart Document Workspace)**
   - Upload course PDFs and study materials.
   - Interact with an AI study assistant powered by **Google Gemini API** (`text-embedding-004` & `gemini-1.5-flash`) that performs similarity-based semantic search over document chunks and provides grounded Q&A with exact page citations.
   - Participate in an interactive **Doubt Board** to ask questions, upvote resources, and mark solutions.

2. **The Marketplace (Peer-to-Peer Peer Handoffs)**
   - Share, request, and hand off physical textbooks, notes, and lab equipment.
   - Backed by an explicit, ACID-compliant **Listing State Machine** (`AVAILABLE` → `REQUESTED` → `GIVEN_AWAY`) with pessimistic row locking (`select_for_update`) to prevent race conditions during item claims.

---

## 🛠️ Tech Stack Summary

- **Backend**: Python 3.14 / Django 5.1, Django REST Framework, SimpleJWT (Access/Refresh flow), PostgreSQL with `pgvector` (cosine similarity search), Supabase S3-compatible Storage (`django-storages`).
- **Frontend**: React 18 (Vite), Tailwind CSS, Zustand (global state management), Axios (API client), `react-pdf` (PDF viewer).
- **AI & RAG Pipeline**: Google Gemini API (`models/text-embedding-004` for 768-dim embeddings, `models/gemini-1.5-flash` for grounded synthesis).
- **Notifications**: Synchronous in-process event hooks via Django `transaction.on_commit()` for v1 reliability.

---

## 📚 Documentation Index

### Module Readmes
- 🔧 [Backend Documentation](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/README.md) — Django structure, API endpoints, environment configuration, database setup.
- 🎨 [Frontend Documentation](file:///d:/Coding/Projects----For%20Resume/StudyLink/frontend/README.md) — React component architecture, Zustand store, Vite proxy setup.

### Learning Docs (`Learning/`)

#### ⚙️ Backend & Architecture Concepts
- [01. JWT Authentication & Custom User Model](file:///d:/Coding/Projects----For%20Resume/StudyLink/Learning/Backend/01-jwt-authentication-and-custom-user-model.md)
- [02. Listing State Machine & Concurrency Handling](file:///d:/Coding/Projects----For%20Resume/StudyLink/Learning/Backend/02-listing-state-machine-and-concurrency.md)
- [03. pgvector Embeddings & SQLite Compatibility Fallback](file:///d:/Coding/Projects----For%20Resume/StudyLink/Learning/Backend/03-pgvector-embeddings-and-sqlite-fallback.md)
- [04. Gemini API Integration & RAG Pipeline](file:///d:/Coding/Projects----For%20Resume/StudyLink/Learning/Backend/04-gemini-api-and-rag-pipeline.md)
- [05. DRF Architecture: Serializers, ViewSets & Permissions](file:///d:/Coding/Projects----For%20Resume/StudyLink/Learning/Backend/05-drf-architecture-serializers-viewsets-permissions.md)
- [06. Doubt Board & Interactive Q&A Tree](file:///d:/Coding/Projects----For%20Resume/StudyLink/Learning/Backend/06-doubt-board-and-interactive-discussions.md)
- [07. Decoupled Notifications & Transaction Hooks](file:///d:/Coding/Projects----For%20Resume/StudyLink/Learning/Backend/07-decoupled-notifications-and-transaction-hooks.md)

#### 🎨 Frontend Concepts
- [01. React State Management with Zustand](file:///d:/Coding/Projects----For%20Resume/StudyLink/Learning/Frontend/01-react-state-management-and-zustand.md)
- [02. Interactive UI Components: PDF Viewer & RAG Q&A Sidebar](file:///d:/Coding/Projects----For%20Resume/StudyLink/Learning/Frontend/02-interactive-ui-components-pdf-and-rag-chat.md)

#### 🏗️ Infrastructure & Monorepo
- [01. Supabase Storage & S3 API Interoperability](file:///d:/Coding/Projects----For%20Resume/StudyLink/Learning/Infrastructure/01-supabase-s3-interoperability.md)
- [02. Monorepo Architecture & Vite Dev Server Proxying](file:///d:/Coding/Projects----For%20Resume/StudyLink/Learning/Infrastructure/02-monorepo-architecture-and-vite-proxy.md)

---

## ⚡ Quick-Start (Local Development)

### 1. Prerequisites
- Python 3.11+
- Node.js 18+

### 2. Backend Setup
```bash
# Navigate to backend
cd backend

# Create & activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (.env)
cp .env.example .env

# Run database migrations
python manage.py migrate

# Start backend server (port 8000)
python manage.py runserver 8000
```

### 3. Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Vite dev server (port 5173 with proxy to 8000)
npm run dev
```

Visit `http://localhost:5173` to access the application.

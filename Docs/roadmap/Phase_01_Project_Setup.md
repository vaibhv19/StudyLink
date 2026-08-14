# Phase 01 — Project Setup (Monorepo Scaffolding)

This phase establishes the monorepo workspace for **StudyLink**. The project features a split architecture in a single repository: `backend/` containing the Django REST application and `frontend/` containing the React Vite client application.

---

## 1. Module Design: System Foundation Scaffolding

### 1.1 Directory Tree Structure
```text
StudyLink/ (Monorepo Root)
├── .gitignore
├── README.md
├── docker-compose.yml            # Local developer Redis & Dev Services
├── backend/                      # Django REST API application root
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── .gitignore
│   ├── README.md
│   └── config/                   # Django core configuration folder
│       ├── __init__.py
│       ├── settings.py
│       ├── urls.py
│       └── wsgi.py
└── frontend/                     # React Vite frontend application root
    ├── package.json
    ├── tailwind.config.js
    ├── vite.config.js
    ├── postcss.config.js
    ├── .env.example
    ├── .gitignore
    ├── README.md
    ├── public/
    └── src/
```

### 1.2 Purpose
Establish standard, isolated runtime configurations for backend and frontend environments while enabling single-repository developer ergonomics.

### 1.3 Dependencies
- Git (Version Control)
- Python 3.12+ (local runtime)
- Node.js 18+ (local UI runtime)
- Docker (optional, for local Redis service support)

### 1.4 Inputs
- Baseline environment configuration variables (`.env`).

### 1.5 Outputs
- A runnable Django backend structure responding to local HTTP polls.
- A hot-reloading Vite dev server rendering a default layout.

---

## 2. Implementation Hierarchical Breakdown & Tasks

### 2.1 Django Backend Layer (`backend/`)

#### Feature: Directory Initialization
Scaffold the Django project layout and core app folders.

##### Task 01.01.01: Scaffold Django Core config & Apps
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** None
- **Task Description:** Create the `backend/` folder. Initialize virtualenv. Install `django` and `djangorestframework`. Run `django-admin startproject config .` inside `backend/`. Create placeholders for custom apps: `accounts`, `vault`, `market`, and `core`.
- **Definition of Done:**
  - `backend/config/settings.py` is present.
  - Custom applications are registered under `INSTALLED_APPS` (e.g. `accounts.apps.AccountsConfig`).
  - Running `python manage.py check` executes successfully with no configuration errors.

##### Task 01.01.02: Configure Database & Storage Settings
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Task 01.01.01
- **Task Description:** Update `settings.py` to fetch database connections via `dj-database-url` or direct environment injection. Configure variables for Supabase Postgres Transaction Pooler connection parameters (port 6543) and set connection timeout. Enable django-storages S3 configuration templates. Create a `.env.example` in `backend/`.
- **Definition of Done:**
  - Settings file correctly reads database and storage configurations from `os.environ` or a `.env` wrapper.
  - A comprehensive `.env.example` contains all needed database connection variables (e.g., `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`).
  - Attempting to connect to PostgreSQL with credentials throws standard database errors rather than configuration syntax bugs.

##### Task 01.01.03: Set Up Global Middleware, REST Framework & SimpleJWT base settings
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 01.01.01
- **Task Description:** Inject `rest_framework` and standard REST configurations in `settings.py`. Configure default permission classes to `rest_framework.permissions.IsAuthenticated` (by default, APIs are protected unless overridden). Define base configuration fields for `SimpleJWT` token lifespan settings.
- **Definition of Done:**
  - REST framework setting dict is defined in `settings.py`.
  - SimpleJWT tokens configured (access: 15 minutes, refresh: 7 days).
  - Backend runs clean with zero startup runtime errors.

---

### 2.2 React Frontend Layer (`frontend/`)

#### Feature: Vite Scaffolding
Scaffold the frontend react runtime environment.

##### Task 01.02.01: Scaffold React Vite Project
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** None
- **Task Description:** Run `npm create vite@latest frontend -- --template react` in the monorepo root. Clean up default assets in `src/` to yield a blank layout structure. Create `.env.example` defining `VITE_API_BASE_URL`.
- **Definition of Done:**
  - `frontend/package.json` contains Vite dependencies.
  - Running `npm run dev` in `frontend/` launches the development server on localhost.

##### Task 01.02.02: Install Core Frontend Libraries & Router Scaffolding
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 01.02.01
- **Task Description:** Install frontend dependencies: `react-router-dom`, `zustand`, `axios`, and class merge helpers (`clsx`, `tailwind-merge`). Configure baseline Router settings under `src/main.jsx`.
- **Definition of Done:**
  - Package listings in `package.json` reflect target versions.
  - Router framework loads without console errors on startup.

##### Task 01.02.03: Configure Tailwind CSS & Design System Tokens
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 01.02.01
- **Task Description:** Install Tailwind CSS, PostCSS, and Autoprefixer. Run `npx tailwindcss init -p` to output configs. In `tailwind.config.js`, inject typography variables, borders, custom color variables representing "Digital Campus" palette (Royal Purple primary: `#6366f1`, Teal/Cyan accent: `#06b6d4`, Surface backgrounds: `#ffffff`). Import tailwind direct directives in `src/index.css`.
- **Definition of Done:**
  - `tailwind.config.js` lists custom colors and font families.
  - Running `npm run build` generates production assets applying Tailwind utility classes.

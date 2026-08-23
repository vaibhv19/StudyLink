# Phase 12 — Future Manual Cloud Deployment Guide (Reference Guide)

> **Status Notice (v1):** Active public cloud deployment is **INTENTIONALLY DEFERRED** for the StudyLink v1 release (Deployment: ❎, Deployment Documentation: ❎). This step-by-step deployment guide is preserved as an architectural reference for future deployment to Google Cloud Run and Vercel in v2.

This phase covers manual cloud deployment steps for **StudyLink** when deploying to GCP Cloud Run, Supabase Postgres & Storage, Gemini API keys, and Vercel static hosting.

*Note: OAuth Consent Screen setup and custom domain/DNS setup steps are excluded for v1.*

---

## 1. Supabase Project Setup

### Step 1.1: Create Project & Database
- **Purpose:** Set up the PostgreSQL database and connection pool.
- **Where to navigate:** [Supabase Dashboard](https://supabase.com/dashboard) → **New Project**.
- **Information required:** Project Name (`studylink`), Database Password, Region closest to deployment.
- **Expected outcome:** Database spins up and displays connection details.
- **Verification checklist:**
  - [ ] Database is running.
  - [ ] Connection string for the Transaction Pooler (port 6543) is copied.
- **Common mistakes:** Copying the direct connection string (port 5432) instead of the transaction pooler (port 6543), which can exhaust connections in serverless environments.
- **Next dependent step:** Step 1.2.

### Step 1.2: Enable `pgvector` Extension
- **Purpose:** Enable vector storage.
- **Where to navigate:** Supabase Dashboard → **SQL Editor** → **New Query**.
- **Information required:** SQL Command: `CREATE EXTENSION IF NOT EXISTS vector;`.
- **Expected outcome:** Query runs successfully.
- **Verification checklist:**
  - [ ] `pgvector` extension is active.
- **Common mistakes:** Forgetting to run this query before applying Django migrations, which causes migrations to fail.
- **Next dependent step:** Step 1.3.

### Step 1.3: Create Storage Buckets & Policies
- **Purpose:** Create storage buckets for PDFs and listing photos.
- **Where to navigate:** Supabase Dashboard → **Storage** → **New Bucket**.
- **Information required:**
  - Bucket 1: `resources` (Public: Off).
  - Bucket 2: `listings` (Public: On).
- **Expected outcome:** Buckets are created. Configure policies to allow public read access for listings and authenticated write access for both buckets.
- **Verification checklist:**
  - [ ] Buckets display in the storage dashboard.
  - [ ] Storage policies are configured.
- **Common mistakes:** Setting the `resources` bucket to public, exposing private notes to unauthorized users.
- **Next dependent step:** Section 2.

---

## 2. Google Cloud Platform Setup

### Step 2.1: Enable APIs & Services
- **Purpose:** Enable services required for Cloud Run deployment.
- **Where to navigate:** GCP Console → **APIs & Services** → **Library**.
- **Information required:** Search and enable:
  - Cloud Run API
  - Artifact Registry API
  - Cloud Build API
  - Secret Manager API
- **Expected outcome:** APIs are active.
- **Verification checklist:**
  - [ ] APIs display in the enabled services list.
- **Common mistakes:** Deploying the backend before enabling these APIs, which causes build errors.
- **Next dependent step:** Step 2.2.

### Step 2.2: Create Artifact Registry Repository
- **Purpose:** Create a registry to store the backend Docker image.
- **Where to navigate:** GCP Console → **Artifact Registry** → **Create Repository**.
- **Information required:** Name (`studylink-repo`), Format (Docker), Region.
- **Expected outcome:** Repository is created.
- **Verification checklist:**
  - [ ] Repository is available.
- **Next dependent step:** Step 2.3.

### Step 2.3: Deploy Django Backend to Cloud Run
- **Estimated Size:** L
- **Risk:** High
- **Prerequisites:** Task 11.01.01, Step 2.2
- **Task Description:** Build and push the Docker image to Artifact Registry, then deploy it to Cloud Run using Secret Manager to store sensitive variables (DATABASE_URL, SECRET_KEY, GEMINI_API_KEY). Use Cloud Run's default assigned `*.run.app` URL.
- **Definition of Done:**
  - Service is active and returns a default `https://<service-name>-<hash>.run.app` URL.
  - `/api/v1/core/courses/` endpoint returns seeded academic tags.
- **Common mistakes:** Storing database passwords in plain text instead of using GCP Secret Manager.
- **Next dependent step:** Section 3.

---

## 3. Vercel Frontend Deployment

### Step 3.1: Deploy React App to Vercel
- **Purpose:** Compile and host the frontend client on Vercel's default domain.
- **Where to navigate:** [Vercel Dashboard](https://vercel.com) → **Add New** → **Project**.
- **Information required:** Link to the GitHub repository, then configure build settings:
  - Framework Preset: `Vite`
  - Root Directory: `frontend`
  - Build Command: `npm run build`
  - Output Directory: `dist`
  - Environment Variable: `VITE_API_BASE_URL` set to the Cloud Run backend URL (`https://<service-name>-<hash>.run.app`).
- **Expected outcome:** Vercel builds the app and returns a default production URL (`https://<project-name>.vercel.app`).
- **Verification checklist:**
  - [ ] Build succeeds.
  - [ ] App displays in the browser.
- **Common mistakes:** Leaving the root directory set to the repository root instead of `frontend/`, which causes build failures.
- **Next dependent step:** Section 4.

---

## 4. Handshake Verification

### Step 4.1: Update CORS Settings
- **Purpose:** Complete the handshake by adding the frontend default Vercel URL to the backend's allowed origins.
- **Where to navigate:** GCP Console → **Cloud Run** → Select backend service → **Edit & Deploy New Revision**.
- **Information required:** Update `CORS_ALLOWED_ORIGINS` to include the default Vercel production and preview URLs.
- **Expected outcome:** Backend accepts requests from the frontend app.
- **Verification checklist:**
  - [ ] Frontend can authenticate via JWT, upload notes synchronously, and make marketplace requests.
- **Common mistakes:** Omitting the `https://` prefix in allowed CORS origins.

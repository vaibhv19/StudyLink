# Learning Doc 11: Monorepo Architecture & Vite Dev Server Proxying

> **Topic**: Single-Repository Organization, Reverse-Proxy Development Architecture, CORS Elimination, and Multi-Cloud Deployment Routing.

---

## 1. Problem / Concept

When building full-stack applications with separate frontend and backend technologies (e.g. React SPA + Django REST API), developers face two major structural questions:
1. **Repository Layout**: Should frontend and backend live in separate repositories or share a single repository (**monorepo**)?
2. **Local Development Proxying**: How do we prevent Cross-Origin Resource Sharing (CORS) friction and port mismatches when running React on port `5173` and Django on port `8000`?

---

## 2. How It Works Generally

- **Monorepo Advantages**: Keeping `backend/` and `frontend/` in one repository ensures atomic git commits, single-source-of-truth documentation, and unified issue tracking.
- **Dev Server Reverse-Proxying**: Development servers (such as Vite) feature built-in HTTP proxying. Requests originating from the browser to `/api/*` are intercepted by the Vite dev server on port `5173` and proxied behind the scenes to `http://localhost:8000/api/*`.
- **CORS Elimination**: Because the browser only talks to `localhost:5173`, requests appear same-origin during development, eliminating CORS pre-flight browser blocks.

---

## 3. How StudyLink Specifically Uses It

In `frontend/vite.config.js`, `docker-compose.yml`, and `vercel.json`:

- **Vite Proxy Config (`frontend/vite.config.js`)**:
  ```js
  export default defineConfig({
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
        '/media': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        }
      }
    }
  })
  ```
- **Deployment Decoupling (Prepared Architecture)**:  
  - **Frontend**: Configured for Vercel via root `vercel.json` SPA rewrites (`"src": "/(.*)", "dest": "/index.html"`).
  - **Backend**: Containerized via `backend/Dockerfile` and `docker-compose.yml` for serverless container deployment (e.g. GCP Cloud Run).
  - *v1 Release Note:* Active public hosting is intentionally deferred; the application is fully container-ready.

---

## 4. Key Files & Code References

- [frontend/vite.config.js](file:///d:/Coding/Projects----For%20Resume/StudyLink/frontend/vite.config.js#L1-L23) — Vite proxy setup for `/api` and `/media`.
- [docker-compose.yml](file:///d:/Coding/Projects----For%20Resume/StudyLink/docker-compose.yml#L1-L20) — Docker Compose service orchestrator.
- [vercel.json](file:///d:/Coding/Projects----For%20Resume/StudyLink/vercel.json#L1-L15) — Vercel routing rules.

---

## 5. Interview Deep-Dive Takeaways

> [!TIP]
> **What to highlight in an interview:**
> 1. **Why Vite Proxy for Local Dev?**  
>    "Using Vite's dev proxy allows frontend components to make clean, domain-relative requests (`axios.get('/api/v1/...')`). This ensures identical API call code works in both local development and production environments."
> 2. **Monorepo Simplicity**:  
>    "A monorepo structure allows full-stack changes (such as adding a new API endpoint in Django and consuming it in React) to be reviewed and committed in a single atomic git commit."

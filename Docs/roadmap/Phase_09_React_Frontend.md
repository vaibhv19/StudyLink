# Phase 09 — React Frontend UI

This phase implements the client-side single page application (SPA) for **StudyLink** using React 18, Vite, Zustand, React Router 6, and Tailwind CSS.

---

## 1. Module Design: `frontend` App

### 1.1 Folder Structure
```text
frontend/
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── Navbar.jsx
│   │   ├── FilterSidebar.jsx
│   │   ├── ProtectedRoute.jsx
│   │   └── ChatSidebar.jsx
│   ├── context/ / store/
│   │   ├── authStore.js        # Auth state (JWT access token in memory)
│   │   └── filterStore.js      # Global subject/course filter state
│   ├── pages/
│   │   ├── Auth.jsx            # Login & Register views (Email/Password JWT)
│   │   ├── ResourceVault.jsx   # Vault grid & Doubt Board
│   │   ├── Marketplace.jsx     # Listings & Request Modal
│   │   └── Dashboard.jsx       # Owner listings & incoming requests
│   ├── services/
│   │   └── api.js              # Axios instance with Bearer auth & refresh interceptor
│   ├── App.jsx
│   └── main.jsx
```

---

## 2. Implementation Tasks

### 2.1 React Frontend Layer (`frontend/`)

#### Feature: Axios API Client & Auth Store
Build core state management.

##### Task 09.01.01: Configure Axios Interceptor & Zustand `authStore`
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Phase 02 complete
- **Task Description:** Create `authStore.js` managing access token in memory and user profile state. Create Axios client with `Authorization: Bearer <access>` header and automatic token refresh interceptor on HTTP 401 responses.
- **Definition of Done:**
  - Login stores access token; 401 response triggers `/auth/token/refresh/` cookie call seamlessly.

##### Task 09.01.02: Build Auth Page (Login & Register)
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Task 09.01.01
- **Task Description:** Build `Auth.jsx` with tabs for Login and Register using standard email/password inputs.
- **Definition of Done:**
  - Users can register and log in, updating `authStore` and redirecting to `/vault`.

##### Task 09.01.03: Build Shared Filter Sidebar & Navigation
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 09.01.01
- **Task Description:** Implement persistent `FilterSidebar.jsx` connected to `filterStore.js` for subject and course selection across Vault and Marketplace views.
- **Definition of Done:**
  - Selecting a subject updates global filter state across tabs.

##### Task 09.01.04: Build Resource Vault & Doubt Board Views
- **Estimated Size:** L
- **Risk:** Medium
- **Prerequisites:** Phase 04 & 07 complete
- **Task Description:** Implement `ResourceVault.jsx` with resource grid, PDF upload modal, Doubt Board comment thread, upvote button, and scoped Chat Sidebar.
- **Definition of Done:**
  - Uploading a PDF refreshes the grid; clicking "Chat with Notes" opens the RAG chat sidebar.

##### Task 09.01.05: Build Marketplace & Owner Dashboard Views
- **Estimated Size:** L
- **Risk:** Medium
- **Prerequisites:** Phase 05 complete
- **Task Description:** Implement `Marketplace.jsx` for browsing listings and sending requests, and `Dashboard.jsx` for owners to accept/reject pending item requests.
- **Definition of Done:**
  - Item requests display in owner dashboard; accepting a request updates listing state.

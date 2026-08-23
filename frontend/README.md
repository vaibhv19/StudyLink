# StudyLink Frontend

> React 18 single-page application built with Vite, Tailwind CSS, and Zustand for the StudyLink academic collaboration platform.

---

## 🎨 Application Architecture

```
frontend/src/
├── components/          # Reusable UI components
│   ├── PdfViewer.jsx    # Client-side canvas PDF document reader (`react-pdf`)
│   ├── RagChatPanel.jsx # Side-by-side RAG Q&A sidebar with page citation jumping
│   ├── DoubtBoard.jsx   # Nested comment tree with solution marking
│   ├── FilterSidebar.jsx# Subject, course, and text search filter controls
│   ├── Navbar.jsx       # Header navigation & notification dropdown
│   └── ProtectedRoute.jsx# Auth wrapper for protected pages
├── pages/               # Page views matching core application modules
│   ├── Home.jsx         # Landing page & feature showcase
│   ├── ResourceVault.jsx# Vault module: document grid & upload modal
│   ├── ResourceDetail.jsx# Interactive document workspace (PDF + RAG + Doubt Board)
│   ├── Marketplace.jsx  # Marketplace module: item listing grid & request modal
│   ├── ListingDetail.jsx# Listing detail & claim request view
│   ├── OwnerDashboard.jsx# Owner dashboard: manage listings & outgoing requests
│   └── Auth.jsx         # Login & registration forms
├── store/               # Global state stores (Zustand)
│   ├── authStore.js     # User session, JWT tokens, login/logout state
│   └── filterStore.js   # Filter parameters (subject, course, search query)
└── vite.config.js       # Vite build & reverse-proxy configuration
```

---

## 🔄 Backend Dev Server Proxying

To avoid CORS friction during local development, `vite.config.js` routes API requests directly to the Django backend running on port 8000:

```js
// vite.config.js snippet
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

All API requests in the frontend use relative paths (`/api/v1/...`), which seamlessly resolve to `http://localhost:8000/api/v1/...` in development and to the production domain when deployed.

---

## ⚡ Setup & Commands

```bash
# Install dependencies
npm install

# Start development server (http://localhost:5173)
npm run dev

# Run unit / component tests
npm test

# Build production bundle
npm run build
```

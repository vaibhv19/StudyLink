# Phase 09 — React Frontend UI

This phase implements the frontend client application for **StudyLink**. It covers React Router 6 setups, Zustand state stores, auth pages (with OAuth callback and linking modal UI), the Resource Vault grid, the PDF Viewer & Chat panel (RAG interface), the Marketplace browse page, and the Owner Dashboard.

---

## 1. Module Design: `frontend` React App

### 1.1 Source Directory Structure
```text
frontend/src/
├── main.jsx                    # Vite entrance file
├── App.jsx                     # Route bindings and global layouts
├── index.css                   # Tailwind imports and design variables
├── components/                 # Shared UI elements
│   ├── Button.jsx
│   ├── Card.jsx
│   ├── Badge.jsx               # Marketplace status badges
│   ├── UpvoteButton.jsx        # Pill shape [▲ | 42]
│   └── FilterSidebar.jsx       # Persistent tags selector
├── context/
├── hooks/
│   └── useApi.js               # Axios instance configuration
├── pages/                      # Feature views
│   ├── Auth.jsx                # Login / Registration view
│   ├── OAuthCallback.jsx       # Intercepts provider auth codes
│   ├── AccountLinkModal.jsx    # Pop-up for linking accounts
│   ├── ResourceVault.jsx       # Library browse grid
│   ├── ResourceDetail.jsx      # PDF Viewer + Chat view
│   ├── Marketplace.jsx         # Classifieds masonry search list
│   ├── CreateListing.jsx       # Upload listing form wizard
│   └── OwnerDashboard.jsx      # Carousel and requests panel
├── store/                      # Zustand global state managers
│   ├── authStore.js            # In-memory JWT access token & profile
│   └── filterStore.js          # Shared subject/course filter options
└── utils/
```

### 1.2 Purpose
Provides a client-side interface for StudyLink, utilizing the "Digital Campus" design palette (Royal Purple `#6366f1` and Teal/Cyan `#06b6d4`) to deliver a smooth user experience.

### 1.3 Dependencies
- `react-router-dom` (Routing engine)
- `zustand` (State management)
- `axios` (HTTP client)
- `tailwindcss` (Styling utility framework)

### 1.4 Inputs
- User events, form inputs, and document uploads.
- JSON responses from the Django backend.

### 1.5 Outputs
- Compiled static assets hosted on the web.
- Localized browser navigation states.

---

## 2. Implementation Tasks

### 2.2 React Frontend Layer (`frontend/`)

#### Feature: Routing & Zustand Setup
Configure the core application routing and state stores.

##### Task 09.02.01: Configure React Router 6 & Layout Wrappers
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Phase 01 complete
- **Task Description:** In `src/App.jsx`, implement routes: `/auth`, `/oauth-callback`, `/vault`, `/vault/:id`, `/market`, `/market/:id`, `/dashboard`, and `/dashboard/owner`. Implement shared layout templates with a top navigation bar and footer.
- **Definition of Done:**
  - Manually navigating to paths loads the correct page component.
  - Unauthorized requests to `/dashboard` route back to `/auth`.

##### Task 09.02.02: Implement Zustand `authStore` & Axios Client Hook
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Task 09.02.01
- **Task Description:** Implement `authStore.js` managing the `accessToken` in memory, the user profile object, and login/logout methods. Create an Axios instance that attaches the JWT header (`Authorization: Bearer <token>`) and intercepts 401 errors to refresh the token using cookie rotation.
- **Definition of Done:**
  - Authenticating updates the Zustand store and automatically attaches headers to subsequent API calls.
  - Refresh tokens are verified under the hood when access tokens expire.

#### Feature: Authentication Interface
Develop registration and login views.

##### Task 09.02.03: Build Login & Registration View with OAuth links
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Task 09.02.02
- **Task Description:** Design the UI on `/auth` using the Digital Campus design palette (Royal Purple gradients and satoshi fonts). Provide forms for login and registration, and add Google/GitHub buttons that route users to provider auth screens.
- **Definition of Done:**
  - Email/password registration and login work correctly.
  - Clicking OAuth buttons redirects users to Google/GitHub authentication screens.

##### Task 09.02.04: Implement Account Link Confirmation Modal
- **Estimated Size:** M
- **Risk:** Medium
- **Prerequisites:** Task 09.02.03
- **Task Description:** Build a modal pop-up on `/oauth-callback`. If the backend returns a 409 Conflict indicating that the email matches an existing local account, prompt the user to enter their password to link their accounts.
- **Definition of Done:**
  - Successfully entering the local password links the account and redirects the user to their dashboard.

#### Feature: Digital Resource Vault UI
Develop the resource vault search interfaces and RAG panels.

##### Task 09.02.05: Build Vault Discovery Grid & Filter Sidebar
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Task 09.02.02
- **Task Description:** Build `/vault` view. The screen consists of a persistent filter sidebar (subject, course search) and a high-density grid showing resource cards (file type icon, upvote count pill, and status badges). Add a multipart PDF upload form.
- **Definition of Done:**
  - App displays lists of uploaded resources, and selecting sidebar filters updates the view immediately.
  - Uploading a PDF updates the feed and displays a `PROCESSING` badge.

##### Task 09.02.06: Implement Split PDF Viewer & RAG Chat Sidebar Panel
- **Estimated Size:** L
- **Risk:** High
- **Prerequisites:** Task 09.02.05
- **Task Description:** Build `/vault/:id` view.
  - **Left (70%):** Interactive PDF Viewer.
  - **Right (30%):** Chat panel (only enabled when status is `READY`).
  - Render user message bubbles and AI answers. Render citations below AI responses as small clickable page number cards that scroll the PDF to the corresponding page.
  - Render the Doubt Board threaded comment interface below the page layout.
- **Definition of Done:**
  - Chatting with notes displays AI answers and citations.
  - Clicking a citation card changes the active page in the PDF Viewer.

#### Feature: Marketplace Classifieds UI
Build classified search screens.

##### Task 09.02.07: Build Marketplace Classifieds Grid & Creation form wizard
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Task 09.02.02
- **Task Description:** Implement `/market` browse grid emphasizing photos and pickup area tags. Add a listing creation form featuring photo previews, condition options, and pickup area fields.
- **Definition of Done:**
  - Lists and detail pages render photos and listing details.
  - Posting a listing uploads the details and displays the new item.

##### Task 09.02.08: Implement Listing Request Panel
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 09.02.07
- **Task Description:** On the listing detail page, show a "Request Item" action button. For the owner, display a link to the owner dashboard instead.
- **Definition of Done:**
  - Non-owners can click the button to send a request, which updates the UI to show the request is pending.

#### Feature: Owner Dashboard UI
Build the marketplace coordination console.

##### Task 09.02.09: Build Owner Dashboard view
- **Estimated Size:** M
- **Risk:** Medium
- **Prerequisites:** Task 09.02.02
- **Task Description:** Build `/dashboard/owner` split view.
  - **Top:** "Your Listings" Carousel displaying items with status badges (`AVAILABLE` in green, `REQUESTED` in amber, `GIVEN AWAY` in gray).
  - **Bottom:** "Pending Requests" list, grouped by listing, showing the name of each requester and Accept/Decline action buttons.
  - If a listing is `REQUESTED`, display the recipient's contact details and a "Confirm Handoff" button.
- **Definition of Done:**
  - Accept/Decline and Confirm Handoff actions function correctly, updating status badges and listing states in the view immediately.

##### Task 09.02.10: Write Frontend UI Verification Tests
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 09.02.09
- **Task Description:** Write tests to check router layouts, Zustand stores, and component rendering states.
- **Definition of Done:**
  - Test suites execute and pass successfully.

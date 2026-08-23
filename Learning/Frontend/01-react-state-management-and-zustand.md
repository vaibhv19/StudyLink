# Learning Doc 08: React State Management with Zustand

> **Topic**: Lightweight Global State, Token Persistence, Reactive Filter Filtering, and Component Re-render Optimization in React 18.

---

## 1. Problem / Concept

In modern Single Page Applications (SPAs), state falls into two categories:
1. **Local Component State**: Transient UI state (e.g. modal visibility, form input fields).
2. **Global Application State**: State shared across completely separate view hierarchies (e.g. user authentication tokens, active filter criteria across navigation bars and catalog pages).

Passing global state down through multiple tiers of intermediate React components via props ("prop-drilling") makes code rigid and difficult to maintain. Using React Context for rapidly changing state can trigger unwanted component re-renders across the entire component tree.

---

## 2. How It Works Generally

**Zustand** is a un-opinionated, lightweight state management library for React. Key benefits include:
- **Zero Boilerplate**: Defined using a simple `create()` store hook function without context providers or complex reducers.
- **Selector-Based Subscriptions**: Components subscribe to explicit slices of state (e.g. `const user = useAuthStore(state => state.user)`). Components re-render **only** when their selected slice changes.
- **Out-of-React Updates**: Stores can be read or mutated outside React components (e.g. inside Axios request/response interceptors).

---

## 3. How StudyLink Specifically Uses It

In `frontend/src/store/`:

- **Authentication Store (`authStore.js`)**:
  ```js
  import { create } from 'zustand';

  export const useAuthStore = create((set, get) => ({
    user: null,
    accessToken: null,
    isAuthenticated: false,

    login: (userData, accessToken) => {
      set({ user: userData, accessToken, isAuthenticated: true });
    },
    logout: () => {
      set({ user: null, accessToken: null, isAuthenticated: false });
    },
    setAccessToken: (accessToken) => {
      set({ accessToken, isAuthenticated: !!accessToken });
    },
  }));
  ```
- **Filter Store (`filterStore.js`)**:
  Manages search parameters across the Resource Vault: `selectedSubject`, `selectedCourse`, `searchQuery`, and `setSubject()`, `setCourse()`, `setSearchQuery()`, `resetFilters()`.
- **API Interceptor Integration**:
  The Axios client reads `useAuthStore.getState().accessToken` to attach `Authorization: Bearer <token>` headers to outgoing requests without requiring React component lifecycle hooks.

---

## 4. Key Files & Code References

- [frontend/src/store/authStore.js](file:///d:/Coding/Projects----For%20Resume/StudyLink/frontend/src/store/authStore.js#L1-L44) — `useAuthStore` managing session and JWT tokens.
- [frontend/src/store/filterStore.js](file:///d:/Coding/Projects----For%20Resume/StudyLink/frontend/src/store/filterStore.js#L1-L30) — `useFilterStore` managing subject/course/search filters.
- [frontend/src/pages/Auth.jsx](file:///d:/Coding/Projects----For%20Resume/StudyLink/frontend/src/pages/Auth.jsx#L1-L150) — Component consuming `useAuthStore` during login and registration.

---

## 5. Interview Deep-Dive Takeaways

> [!TIP]
> **What to highlight in an interview:**
> 1. **Why Zustand over Redux or React Context?**  
>    "Zustand eliminates Redux boilerplate while avoiding React Context's re-render pitfalls. Its selector subscription pattern ensures components re-render strictly when their selected state slice mutates."
> 2. **Reading State Outside React Render Loops**:  
>    "Because Zustand stores expose `getState()`, non-React modules like API utility functions and Axios interceptors can read authentication tokens directly without needing React custom hooks."

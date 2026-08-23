# Phase 10 — Integration Testing

This phase covers end-to-end (E2E) testing and integration verification for **StudyLink**. It validates user registration, JWT token refresh, resource uploading, synchronous RAG retrieval, marketplace state transitions, and owner dashboard workflows.

---

## 1. Test Suite Structure

```text
tests/
├── e2e/
│   ├── auth_flow.spec.js       # JWT register, login, refresh E2E tests
│   ├── vault_rag.spec.js       # PDF upload & RAG chat E2E tests
│   └── market_state.spec.js    # Marketplace listing state machine E2E tests
```

---

## 2. Implementation Tasks

##### Task 10.01.01: Implement Auth Flow Integration Tests
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Phase 09 complete
- **Task Description:** Write Playwright/Cypress tests for email/password registration, login token issuance, and refresh token cookie handling.
- **Definition of Done:**
  - Auth test suite passes cleanly.

##### Task 10.01.02: Implement Vault & RAG Chat Integration Tests
- **Estimated Size:** M
- **Risk:** Medium
- **Prerequisites:** Phase 09 complete
- **Task Description:** Write tests for PDF upload, synchronous chunking status `READY`, and RAG query response verification.
- **Definition of Done:**
  - Vault and RAG tests pass cleanly.

##### Task 10.01.03: Implement Marketplace State Machine Integration Tests
- **Estimated Size:** M
- **Risk:** Medium
- **Prerequisites:** Phase 09 complete
- **Task Description:** Test listing creation, requesting item, owner acceptance (`AVAILABLE → REQUESTED → GIVEN AWAY`), and request cancellation fallback.
- **Definition of Done:**
  - Marketplace state machine E2E tests pass cleanly.

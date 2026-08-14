# Phase 10 — Integration & End-to-End Testing

This phase covers building the **Integration & End-to-End Test Suite** for **StudyLink**. It validates cross-layer operations between the React client and the Django REST APIs, verifying RAG chat pipelines, concurrency locking under load, and account linking workflows.

---

## 1. Module Design: E2E Integration Suite

### 1.1 Directory Structure
```text
StudyLink/ (Monorepo Root)
├── tests/                      # Monorepo level E2E testing
│   ├── e2e/
│   │   ├── auth_flow.spec.js   # OAuth, Register & Linking test cases
│   │   ├── vault_rag.spec.js   # PDF upload, status polling & RAG Chat tests
│   │   └── market_state.spec.js# Multi-user requesting & Handoff tests
│   └── package.json
```

### 1.2 Purpose
Ensures system stability by simulating user actions and validating that the API contract and state machine operate correctly.

### 1.3 Dependencies
- Playwright or Cypress (E2E browser test automation)
- Pytest-django (backend test runner)
- `factory_boy` (mock database data generator)

### 1.4 Inputs
- Live test browser sessions.
- Seeded database states.

### 1.5 Outputs
- Test execution reports.
- Visual screenshots showing test results.

---

## 2. Implementation Tasks

### 2.1 Django Backend Layer (`backend/`)

#### Feature: Integration Testing
Test key backend operations and integrations.

##### Task 10.01.01: Write Concurrency Lock Stress Tests
- **Estimated Size:** M
- **Risk:** High
- **Prerequisites:** Phase 05 complete
- **Task Description:** Write a test case in `market/tests/test_concurrency.py` that spawns multiple concurrent threads attempting to accept different requests for the same listing. Verify that the database locks prevent double-acceptance and throw HTTP 409 errors for all subsequent requests.
- **Definition of Done:**
  - Running the concurrency test case passes successfully.

##### Task 10.01.02: Implement PDF Parser Edge Case Tests
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Phase 07 complete
- **Task Description:** Test the PDF parser with different PDF types: clean text files, password-protected files, and scanned images (no text). Verify that scanned images are marked as `UNSEARCHABLE` and password-protected files are handled gracefully.
- **Definition of Done:**
  - Edge-case PDFs are parsed correctly and update the resource status as expected.

##### Task 10.01.03: Build OAuth & Account Linking Integration Tests
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Phase 02 complete
- **Task Description:** Write tests checking the account linking views. Mock Google/GitHub profile responses to test the authentication flow, including password confirmations for existing emails.
- **Definition of Done:**
  - OAuth validation and account linking tests pass successfully.

---

### 2.2 React Frontend Layer (`frontend/`)

#### Feature: E2E Browser Testing
Verify the frontend application flow in the browser.

##### Task 10.02.01: Configure Playwright/Cypress Workspace Scaffolding
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Phase 09 complete
- **Task Description:** Initialize the test framework in the monorepo root. Create test configuration files pointing to target localhost ports.
- **Definition of Done:**
  - Framework executes a baseline test and opens a browser instance.

##### Task 10.02.02: Write Auth & Account Linking E2E test
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Task 10.02.01
- **Task Description:** Write tests to check the authentication flow: registering a user, logging in, and verifying that the account linking modal displays correctly when an email collision occurs.
- **Definition of Done:**
  - Browser tests navigate the authentication screens and verify the workflows.

##### Task 10.02.03: Write Resource Vault PDF Ingestion & Chat E2E test
- **Estimated Size:** M
- **Risk:** Medium
- **Prerequisites:** Task 10.02.01
- **Task Description:** Test the document upload and RAG chat flow: upload a test PDF, wait for status `READY`, type a question in the chat panel, and verify that the AI answer and clickable citations display correctly.
- **Definition of Done:**
  - Uploading a PDF and chatting with it works as expected in the E2E tests.

##### Task 10.02.04: Write Marketplace State Machine E2E test
- **Estimated Size:** M
- **Risk:** Medium
- **Prerequisites:** Task 10.02.01
- **Task Description:** Test the marketplace flow: list an item for giveaway, request the item using a second user account, accept the request from the owner's dashboard, verify that the coordinate details display, and complete the handoff.
- **Definition of Done:**
  - Marketplace transactions are processed correctly in the E2E tests.

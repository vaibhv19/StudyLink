# Phase 02 — Authentication & User Management

This phase covers building the identity layer of **StudyLink**. It implements secure user storage, JWT generation, third-party social logins (Google/GitHub), and the account-linking logic required when an OAuth user’s email collisions occur with existing database records.

---

## 1. Module Design: `accounts` App

### 1.1 Folder Structure
```text
backend/accounts/
├── __init__.py
├── admin.py
├── apps.py
├── models.py                   # CustomUser model definition
├── serializers.py              # User Serializers (Register, Login, Token, Link)
├── services.py                 # Core authentication and provider linking services
├── urls.py                     # Auth URLs (/api/v1/auth/*)
├── views.py                    # Views for Register, Login, OAuth validation, and Linking
└── tests/
    ├── __init__.py
    ├── test_models.py          # CustomUser manager tests
    ├── test_auth.py            # Login & JWT tests
    └── test_oauth.py           # Linking logic mock tests
```

### 1.2 Purpose
Handles identity registration, token management, third-party profile retrieval, and account merging.

### 1.3 Dependencies
- `djangorestframework-simplejwt` (JSON Web Token authentication backend)
- `requests` (for requesting provider APIs during OAuth verification)
- `core` module (for global error responses)

### 1.4 Inputs
- User registration forms (email, password, name)
- OAuth auth codes (Google, GitHub)
- HTTP authorization header credentials (`Bearer <token>`)

### 1.5 Outputs
- Signed access/refresh tokens.
- Populated `users` database records.
- Standardized OAuth payload responses.

### 1.6 Classes, Methods & Serialization Mappings

#### Model: `CustomUser` (inherits from `AbstractBaseUser`, `PermissionsMixin`)
- **Fields:**
  - `id`: `models.UUIDField` (default `uuid.uuid4`, primary key)
  - `email`: `models.EmailField` (unique, indexed)
  - `password`: `models.CharField` (nullable)
  - `provider`: `models.CharField` (choices: `local`, `google`, `github`, default `local`)
  - `linked_google`: `models.BooleanField` (default `False`)
  - `linked_github`: `models.BooleanField` (default `False`)
  - `full_name`: `models.CharField` (max_length=100)
  - `avatar_url`: `models.URLField` (nullable)
  - `is_active`: `models.BooleanField` (default `True`)
  - `is_staff`: `models.BooleanField` (default `False`)
- **Manager:** `CustomUserManager` (implements `create_user` and `create_superuser`)

#### Services:
- `accounts.services.AuthService.authenticate_local_user(email, password)`
- `accounts.services.OAuthService.verify_google_token(auth_code)`
- `accounts.services.OAuthService.verify_github_token(auth_code)`
- `accounts.services.AccountLinkService.link_provider_to_local_account(user, provider, profile_data)`

#### Serializers:
- `RegisterSerializer`: Validates email formats and password strengths.
- `UserDetailSerializer`: Returns ID, email, name, avatar, and linked providers.
- `OAuthCallbackSerializer`: Parses incoming provider codes.
- `AccountLinkConfirmSerializer`: Validates username/password combinations during explicit account merging.

---

## 2. Implementation Tasks

### 2.1 Django Backend Layer (`backend/`)

#### Feature: Custom User Model & DB Scaffolding
Establish the database user model.

##### Task 02.01.01: Implement `CustomUser` Model & Custom Manager
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Phase 01 complete
- **Task Description:** Define the `CustomUser` class and its manager class inside `accounts/models.py`. Ensure that `password` can be null for OAuth signups. Point `AUTH_USER_MODEL` in `settings.py` to `accounts.CustomUser`. Generate and run initial DB migrations.
- **Definition of Done:**
  - Initial migrations run successfully.
  - Creating a user using Django CLI `createsuperuser` operates cleanly and inserts a UUID-keyed record.

##### Task 02.01.02: Integrate SimpleJWT configurations & Token Issuing endpoints
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 02.01.01
- **Task Description:** Set up standard Django routing endpoints `/api/v1/auth/token/refresh/` mapping to `TokenRefreshView`. Write a custom login serializer that issues access tokens in JSON payloads and sets the refresh token as a secure, `HttpOnly` cookie.
- **Definition of Done:**
  - Logging in with standard credentials returns `access` in JSON and sets a cookie for `refresh_token`.
  - POSTing the cookie token to the refresh URL generates a new access token.

#### Feature: Registration API & Validation
Configure basic registration services.

##### Task 02.01.03: Create Register API View & Serializer with Email Collisions checks
- **Estimated Size:** M
- **Risk:** Medium
- **Prerequisites:** Task 02.01.02
- **Task Description:** Implement `/api/v1/auth/register/` endpoint. If an email address already exists and is associated with a local provider account, return `400 Bad Request`. If the email exists but has *only* oauth provider flags set (e.g. `provider = google`), return a `409 Conflict` containing guidance mapping to instructions to link the account.
- **Definition of Done:**
  - Standard user registration creates a database row with hashed passwords.
  - Submitting an existing OAuth-only email yields a HTTP 409 response instructing the client to link profiles.

#### Feature: Third-Party OAuth & Account Linking
Build Google/GitHub OAuth integrations.

##### Task 02.01.04: Implement Google & GitHub Profile verification services
- **Estimated Size:** M
- **Risk:** Medium
- **Prerequisites:** Task 02.01.01
- **Task Description:** Write `verify_google_token` and `verify_github_token` methods in `accounts/services.py`. These methods must mock or call provider APIs using backend keys, exchanging code queries for profiles (containing `email`, `id`, `name`, `avatar_url`).
- **Definition of Done:**
  - Profile retrieval returns structured user identity dicts.
  - Failure responses from third-party APIs (invalid tokens, timeouts) raise custom exceptions caught by global handlers.

##### Task 02.01.05: Implement OAuth Callback Login endpoint
- **Estimated Size:** M
- **Risk:** Medium
- **Prerequisites:** Task 02.01.04
- **Task Description:** Create `/api/v1/auth/social/google/` and `/api/v1/auth/social/github/` routes. When a code arrives, retrieve the profile. If the user does not exist, create a password-less record. If the email exists, trigger account merging checks.
- **Definition of Done:**
  - Google/GitHub authentication logs a user in, yielding a JWT.
  - Existing local accounts with matching emails block auto-login, redirecting to confirmation steps.

##### Task 02.01.06: Implement Account Linking Logic view
- **Estimated Size:** M
- **Risk:** High
- **Prerequisites:** Task 02.01.05
- **Task Description:** Create `/api/v1/auth/social/link-confirm/` endpoint. If the user is prompted with a 409 collision, they send their existing local password alongside the OAuth identifier code. The service verifies the password, then marks the user model’s flags (`linked_google = True` or `linked_github = True`) and returns a JWT session.
- **Definition of Done:**
  - Submitting a correct local password links the OAuth identity to the existing user.
  - Submitting an incorrect password returns `401 Unauthorized` without modifying the model.

##### Task 02.01.07: Write Unit & Integration Tests for Auth Flow
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Task 02.01.06
- **Task Description:** Implement comprehensive tests inside `accounts/tests/`. Mock remote Google/GitHub HTTP responses using `unittest.mock`. Test registration, token validation, collision handlers, and password-based account linking views.
- **Definition of Done:**
  - All auth tests run via `python manage.py test accounts` and pass cleanly.

# Phase 02 — Authentication & User Management

This phase covers building the identity layer of **StudyLink**. It implements secure user storage, JWT access token generation, refresh token cookies, and standard email/password user registration for v1.

*Note: Third-party social logins (Google/GitHub OAuth) and account-linking flows are deferred to the v2 backlog.*

---

## 1. Module Design: `accounts` App

### 1.1 Folder Structure
```text
backend/accounts/
├── __init__.py
├── admin.py
├── apps.py
├── models.py                   # CustomUser model definition
├── serializers.py              # User Serializers (Register, Login, Token, UserDetail)
├── services.py                 # Core authentication services
├── urls.py                     # Auth URLs (/api/v1/auth/*)
├── views.py                    # Views for Register, Login, Token Refresh
└── tests/
    ├── __init__.py
    ├── test_models.py          # CustomUser manager tests
    └── test_auth.py            # Login & JWT tests
```

### 1.2 Purpose
Handles user registration, identity credentials, SimpleJWT token issuance, and user profile management.

### 1.3 Dependencies
- `djangorestframework-simplejwt` (JSON Web Token authentication backend)
- `core` module (for global error responses)

### 1.4 Inputs
- User registration and login forms (email, password, name)
- HTTP authorization header credentials (`Bearer <token>`)

### 1.5 Outputs
- Signed access tokens (JSON response) and refresh tokens (`HttpOnly` cookie).
- Populated `users` database records.

### 1.6 Classes, Methods & Serialization Mappings

#### Model: `CustomUser` (inherits from `AbstractBaseUser`, `PermissionsMixin`)
- **Fields:**
  - `id`: `models.UUIDField` (default `uuid.uuid4`, primary key)
  - `email`: `models.EmailField` (unique, indexed)
  - `password`: `models.CharField` (hashed)
  - `full_name`: `models.CharField` (max_length=100)
  - `avatar_url`: `models.URLField` (nullable)
  - `is_active`: `models.BooleanField` (default `True`)
  - `is_staff`: `models.BooleanField` (default `False`)
- **Manager:** `CustomUserManager` (implements `create_user` and `create_superuser`)

#### Services:
- `accounts.services.AuthService.authenticate_user(email, password)`

#### Serializers:
- `RegisterSerializer`: Validates email formats, password strength, and uniqueness.
- `LoginSerializer`: Validates incoming login credentials.
- `UserDetailSerializer`: Returns ID, email, full_name, avatar_url.

---

## 2. Implementation Tasks

### 2.1 Django Backend Layer (`backend/`)

#### Feature: Custom User Model & DB Scaffolding
Establish the database user model.

##### Task 02.01.01: Implement `CustomUser` Model & Custom Manager
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Phase 01 complete
- **Task Description:** Define the `CustomUser` class and its manager class inside `accounts/models.py`. Point `AUTH_USER_MODEL` in `settings.py` to `accounts.CustomUser`. Generate and run initial DB migrations.
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

##### Task 02.01.03: Create Register API View & Serializer
- **Estimated Size:** M
- **Risk:** Low
- **Prerequisites:** Task 02.01.02
- **Task Description:** Implement `/api/v1/auth/register/` endpoint. Validate email uniqueness and password strength. If email already exists, return `400 Bad Request`. On successful registration, issue JWT tokens immediately and return `201 Created`.
- **Definition of Done:**
  - Standard user registration creates a database row with hashed passwords.
  - Submitting an existing email yields an HTTP 400 response with descriptive error message.

##### Task 02.01.04: Write Unit Tests for Auth Flow
- **Estimated Size:** S
- **Risk:** Low
- **Prerequisites:** Task 02.01.03
- **Task Description:** Implement comprehensive tests inside `accounts/tests/test_auth.py`. Test registration, token validation, login authentication, and invalid credential failure cases.
- **Definition of Done:**
  - All auth tests run via `python manage.py test accounts` and pass cleanly.

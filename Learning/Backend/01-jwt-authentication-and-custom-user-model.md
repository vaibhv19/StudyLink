# Learning Doc 01: JWT Authentication & Custom User Model

> **Topic**: Authentication, Custom User Extension, and Token Lifecycle Management in Django REST Framework.

---

## 1. Problem / Concept

Traditional web applications rely on **session-based authentication**, where the server stores session IDs in memory or a database and sets a session cookie in the user's browser. While effective for monolithic server-rendered apps, session cookies introduce challenges for modern web architectures:
- **Statelessness**: Distributed APIs and separate frontend apps (like React SPA + Django REST API) require stateless authentication to scale horizontally.
- **CSRF & Cross-Origin Constraints**: Managing session cookies across different domains/origins introduces CORS and CSRF complexity.

**JSON Web Tokens (JWT)** solve this by using cryptographically signed, stateless tokens. The server signs a token containing user claims (e.g. `user_id`, expiration time) and returns it to the client. The client sends this token in the `Authorization: Bearer <token>` HTTP header on subsequent requests.

---

## 2. How It Works Generally

A standard dual-token JWT lifecycle uses two tokens:
1. **Access Token**: Short-lived (e.g. 15 minutes). Sent with API requests. If stolen, the window of vulnerability is minimal.
2. **Refresh Token**: Long-lived (e.g. 7 days). Stored securely. Used solely to obtain a new access token when the current access token expires, without requiring the user to re-enter credentials.

When extending Django's user system, standard Django defaults to an `username` field. Modern applications prefer `email` as the primary unique identifier and require custom fields for OAuth provider integration.

---

## 3. How StudyLink Specifically Uses It

In StudyLink:

- **Custom User Model (`CustomUser`)**: Inherits from `AbstractBaseUser` and `PermissionsMixin`. Replaces `username` with `email` as `USERNAME_FIELD` (`db_index=True`). Tracks OAuth provider integration (`provider` choices: `'local'`, `'google'`, `'github'`) and flags (`linked_google`, `linked_github`).
- **SimpleJWT Integration**: Configured in `config/settings.py` via `rest_framework_simplejwt`. Sets `ACCESS_TOKEN_LIFETIME` to 15 minutes and `REFRESH_TOKEN_LIFETIME` to 7 days. Uses HMAC-SHA256 (`HS256`) signed with Django's `SECRET_KEY`.
- **OAuth Account Linking**: Implemented in `accounts/services.py`, allowing users to register locally or sign in via Google OAuth. If a user signs in with Google using an email that already exists as a local account, StudyLink links the accounts securely.

---

## 4. Key Files & Code References

- [backend/accounts/models.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/accounts/models.py#L31-L55) — `CustomUser` model definition with `email` as `USERNAME_FIELD`.
- [backend/accounts/services.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/accounts/services.py#L1-L100) — Account creation, password hashing, and Google OAuth exchange logic.
- [backend/accounts/views.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/accounts/views.py#L1-L120) — Login, registration, and token refresh API endpoints.
- [backend/config/settings.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/config/settings.py#L189-L208) — SimpleJWT configuration dictionary and DRF default authentication class settings.

---

## 5. Interview Deep-Dive Takeaways

> [!TIP]
> **What to highlight in an interview:**
> 1. **Why `CustomUser` from day 1?**  
>    "Extending `AbstractUser` or `AbstractBaseUser` before initial migrations prevents devastating database refactoring later. Swapping `username` for `email` as the primary identifier is industry standard for consumer and academic apps."
> 2. **Token Security Balance**:  
>    "We use a 15-minute access token combined with a 7-day refresh token. This minimizes the security blast radius of an intercepted access token while maintaining a frictionless user experience."

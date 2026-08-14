"""
Production Settings Override for StudyLink Django Backend.
Target Environment: Google Cloud Run (Serverless Container).
"""

import os
from .settings import *  # noqa: F403

# Production Core Settings
DEBUG = False

# Production Allowed Hosts (read from comma-separated env var or fallback)
ALLOWED_HOSTS_RAW = os.environ.get('ALLOWED_HOSTS', '*')
ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS_RAW.split(',') if h.strip()]

# Static Files Configuration for Production
STATIC_ROOT = BASE_DIR / 'staticfiles'  # noqa: F405

# Production Security & SSL Hardening
# In Google Cloud Run, HTTPS termination happens at the Google Frontend load balancer.
# Cloud Run sets the X-Forwarded-Proto header to 'https'.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True').lower() == 'true'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HTTP Strict Transport Security (HSTS)
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '31536000'))  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Extra Content Security Headers
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

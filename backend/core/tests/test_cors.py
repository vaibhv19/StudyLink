from django.test import TestCase, override_settings
from rest_framework.test import APIClient


class CorsOriginTests(TestCase):
    """
    Verification tests for CORS origin handling, credentials, and domain filtering.
    """

    def setUp(self):
        self.client = APIClient()

    @override_settings(
        CORS_ALLOWED_ORIGINS=['https://studylink.vercel.app', 'https://studylink-app.vercel.app'],
        CORS_ALLOW_ALL_ORIGINS=False,
        CORS_ALLOW_CREDENTIALS=True,
    )
    def test_allowed_origin_returns_cors_headers(self):
        """Requests with an allowed Origin header should receive Access-Control-Allow-Origin."""
        response = self.client.get(
            '/api/v1/core/subjects/',
            HTTP_ORIGIN='https://studylink.vercel.app',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), 'https://studylink.vercel.app')
        self.assertEqual(response.headers.get('Access-Control-Allow-Credentials'), 'true')

    @override_settings(
        CORS_ALLOWED_ORIGINS=['https://studylink.vercel.app'],
        CORS_ALLOW_ALL_ORIGINS=False,
        CORS_ALLOW_CREDENTIALS=True,
    )
    def test_unlisted_origin_blocked_from_cors_headers(self):
        """Requests with an unlisted Origin should NOT receive Access-Control-Allow-Origin header."""
        response = self.client.get(
            '/api/v1/core/subjects/',
            HTTP_ORIGIN='https://unauthorized-domain.com',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.headers.get('Access-Control-Allow-Origin'))

    @override_settings(
        CORS_ALLOWED_ORIGINS=[],
        CORS_ALLOWED_ORIGIN_REGEXES=[r"^https:\/\/.*\.vercel\.app$"],
        CORS_ALLOW_ALL_ORIGINS=False,
        CORS_ALLOW_CREDENTIALS=True,
    )
    def test_vercel_preview_subdomain_cors_regex(self):
        """Dynamic Vercel preview branch deployments matching regex should receive CORS headers."""
        response = self.client.get(
            '/api/v1/core/subjects/',
            HTTP_ORIGIN='https://studylink-feat-deploy-preview.vercel.app',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get('Access-Control-Allow-Origin'),
            'https://studylink-feat-deploy-preview.vercel.app',
        )

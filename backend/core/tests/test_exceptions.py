from django.test import TestCase
from rest_framework.exceptions import ValidationError, AuthenticationFailed, PermissionDenied
from rest_framework.views import APIView
from core.exceptions import custom_exception_handler

class ExceptionHandlerTests(TestCase):
    def test_validation_error_formatting(self):
        exc = ValidationError({"email": ["This field must be unique."]})
        context = {'view': APIView()}
        response = custom_exception_handler(exc, context)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 'validation_error')
        self.assertEqual(response.data['message'], 'Invalid input data.')
        self.assertEqual(response.data['fields']['email'], ["This field must be unique."])

    def test_authentication_error_formatting(self):
        exc = AuthenticationFailed("Invalid access token.")
        context = {'view': APIView()}
        response = custom_exception_handler(exc, context)
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['code'], 'authentication_failed')
        self.assertEqual(response.data['message'], 'Invalid access token.')

    def test_permission_denied_formatting(self):
        exc = PermissionDenied("You do not have permission to view this resource.")
        context = {'view': APIView()}
        response = custom_exception_handler(exc, context)
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['code'], 'permission_denied')
        self.assertEqual(response.data['message'], 'You do not have permission to view this resource.')

    def test_unhandled_python_crash_formatting(self):
        exc = ValueError("Database connection lost.")
        context = {'view': APIView()}
        response = custom_exception_handler(exc, context)
        
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data['code'], 'server_error')
        self.assertEqual(response.data['message'], 'An internal server error occurred on the StudyLink API.')

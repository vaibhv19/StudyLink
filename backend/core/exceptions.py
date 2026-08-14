import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, AuthenticationFailed, PermissionDenied, NotAuthenticated

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    # Call DRF's default exception handler first to get the standard response
    response = exception_handler(exc, context)

    if response is not None:
        data = response.data
        custom_data = {
            "code": "error",
            "message": "An error occurred.",
            "fields": {}
        }
        
        if isinstance(exc, ValidationError):
            custom_data["code"] = "validation_error"
            custom_data["message"] = "Invalid input data."
            if isinstance(data, dict):
                custom_data["fields"] = data
            elif isinstance(data, list):
                custom_data["fields"] = {"non_field_errors": data}
        elif isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
            custom_data["code"] = "authentication_failed"
            custom_data["message"] = data.get('detail') if isinstance(data, dict) else str(data)
        elif isinstance(exc, PermissionDenied):
            custom_data["code"] = "permission_denied"
            custom_data["message"] = data.get('detail') if isinstance(data, dict) else str(data)
        else:
            # Fallback for other standard DRF errors (e.g. NotFound, MethodNotAllowed)
            custom_data["code"] = getattr(exc, 'default_code', 'error')
            custom_data["message"] = data.get('detail') if isinstance(data, dict) else str(data)
            
        response.data = custom_data
    else:
        # Unhandled non-DRF runtime python crashes (HTTP 500)
        logger.exception("Unhandled Server Exception: %s", str(exc))
        response = Response({
            "code": "server_error",
            "message": "An internal server error occurred on the StudyLink API.",
            "fields": {}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response

# server/common/exception_handler.py
from rest_framework.views import exception_handler

from .api_response import ErrorResponse


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF that uses our ErrorResponse.

    Args:
        exc: The exception object
        context: The exception context

    Returns:
        ErrorResponse object with standardized format
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Get the error detail from the response
        detail = response.data

        if isinstance(detail, dict) and 'detail' in detail:
            # Extract the detail text
            detail_text = str(detail['detail'])
            # Remove the detail key
            del detail['detail']
            # If detail was the only key, set detail to the string
            if not detail:
                detail = detail_text

        # Create our standardized error response
        return ErrorResponse(detail=detail, status=response.status_code)

    return response

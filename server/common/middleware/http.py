# server/common/middleware.py
import json

from django.http import HttpRequest, JsonResponse
from rest_framework.exceptions import APIException


class StandardResponseMiddleware:
    """
    Middleware to standardize all API responses.

    This middleware intercepts all JSON responses and formats them according to
    the standard format:
    {
        "state": "success" or "error",
        "message": "A user-friendly message",
        "data": the_response_data
    }

    For error responses, the data may include a "detail" field with
    technical error information.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        response = self.get_response(request)

        # Skip processing for non-API paths if needed
        if not request.path.startswith('/api/'):
            return response

        # Only process JSON responses
        if self._is_json_response(response):
            self._process_response(response)

        return response

    def _is_json_response(self, response):
        """Check if the response is a JSON response."""
        return isinstance(response, JsonResponse) or (
            hasattr(response, 'accepted_media_type')  # type: ignore
            and response.accepted_media_type == 'application/json'
        )

    def _process_response(self, response):
        """Process and standardize the response format."""
        # Skip if already in our format
        if (
            hasattr(response, 'data')
            and isinstance(response.data, dict)
            and 'state' in response.data
        ):
            return

        # Get the response data
        data = self._get_response_data(response)

        # Create the standardized response structure
        success = 200 <= response.status_code < 300

        # Only process successful responses - let ErrorMiddleware handle errors
        if success:
            standardized_data = {
                'state': 'success',
                'message': self._get_default_message(response.status_code),
                'data': data,
            }

            if hasattr(response, 'data'):
                response.data = standardized_data
            else:
                response.content = json.dumps(standardized_data).encode()

    def _get_response_data(self, response):
        """Extract data from the response object."""
        if hasattr(response, 'data'):
            return response.data
        if isinstance(response, JsonResponse):
            return json.loads(response.content.decode('utf-8'))
        return None

    def _get_default_message(self, status_code):
        """Get a default message based on the HTTP status code."""
        if status_code == 200:
            return 'Request processed successfully'
        if status_code == 201:
            return 'Resource created successfully'
        if status_code == 204:
            return 'Resource deleted successfully'
        return 'Request processed successfully'


class ErrorHandlingMiddleware:
    """
    Middleware to handle and standardize error responses.

    This middleware catches exceptions and formats error responses according to
    the standard format:
    {
        "state": "error",
        "message": "A user-friendly error message",
        "data": {
            "detail": "Technical error information"
        }
    }
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as e:
            return self._handle_exception(request, e)

    def _handle_exception(self, request, exception):
        """Handle and format the exception response."""
        if isinstance(exception, APIException):
            status_code = exception.status_code
            detail = str(exception.detail)
        else:
            status_code = 500
            detail = str(exception)

        # Include stack trace in development, but not in production
        # TODO: Add stack trace in development
        error_data = {
            'detail': detail,
        }

        # Get the user-friendly message
        message = self._get_user_friendly_message(status_code)

        # Create standardized error response
        standardized_response = {'state': 'error', 'message': message, 'data': error_data}

        return JsonResponse(standardized_response, status=status_code)

    def _get_user_friendly_message(self, status_code):
        """Get a user-friendly message based on the HTTP status code."""
        if status_code == 400:
            return 'Invalid request data'
        if status_code == 401:
            return 'Authentication required'
        if status_code == 403:
            return "You don't have permission to perform this action"
        if status_code == 404:
            return 'Requested resource not found'
        return "Your request couldn't be processed. Please try again."

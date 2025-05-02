from rest_framework import status as http_status
from rest_framework.response import Response


class ApiResponse(Response):
    """
    A custom response class to standardize API responses.

    Attributes:
        data (dict): The response data payload
        message (str): A user-friendly message
        state (str): The state of the response ("success" or "error")
        status (int): HTTP status code
    """

    def __init__(
        self,
        data=None,
        message=None,
        state='success',
        status=http_status.HTTP_200_OK,
        *args,
        **kwargs,
    ):
        """
        Initialize a standardized API response.

        Args:
            data: The response payload
            message: A user-friendly message
            state: The state of the response (success or error)
            status: HTTP status code
        """
        response_data = {
            'state': state,
            'message': message or self._get_default_message(status),
            'data': data,
        }
        super().__init__(data=response_data, status=status, *args, **kwargs)

    def _get_default_message(self, status):
        """Get a default message based on the HTTP status code."""
        if 200 <= status < 300:
            return 'Request processed successfully'
        if status == http_status.HTTP_400_BAD_REQUEST:
            return 'Invalid request data'
        if status == http_status.HTTP_401_UNAUTHORIZED:
            return 'Authentication required'
        if status == http_status.HTTP_403_FORBIDDEN:
            return "You don't have permission to perform this action"
        if status == http_status.HTTP_404_NOT_FOUND:
            return 'Requested resource not found'
        return 'An error occurred while processing your request'


class ErrorResponse(ApiResponse):
    """
    A specialized response class for error cases that includes a technical message.

    This response includes an additional field for a more detailed technical message
    that would be useful for developers.
    """

    def __init__(
        self,
        message="Your request couldn't be processed. Please try again.",
        detail=None,
        status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
        data=None,
        *args,
        **kwargs,
    ):
        """
        Initialize a standardized error response.

        Args:
            message: A user-friendly error message
            detail: A more technical error message for developers
            status: HTTP status code
            data: Any additional error data
        """
        error_data = {'detail': detail}

        if data:
            if isinstance(data, dict):
                error_data.update(data)
            else:
                error_data['additional_info'] = data

        super().__init__(
            data=error_data, message=message, state='error', status=status, *args, **kwargs
        )

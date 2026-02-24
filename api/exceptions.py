"""
Custom exception handler for API responses.

Provides consistent error responses including rate limiting errors.
"""

from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled
from django.http import JsonResponse


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides better error messages.
    
    Especially useful for throttling/rate limiting errors.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Handle throttling exceptions with custom response
    if isinstance(exc, Throttled):
        wait_time = exc.wait
        
        # Format wait time nicely
        if wait_time:
            if wait_time < 60:
                wait_message = f"{int(wait_time)} seconds"
            elif wait_time < 3600:
                wait_message = f"{int(wait_time / 60)} minutes"
            else:
                wait_message = f"{int(wait_time / 3600)} hours"
        else:
            wait_message = "a moment"
        
        custom_response = {
            'success': False,
            'message': f'Rate limit exceeded. Please try again in {wait_message}.',
            'error': 'too_many_requests',
            'retry_after': int(wait_time) if wait_time else None,
        }
        
        return JsonResponse(custom_response, status=429)
    
    # For other exceptions, return the default response
    if response is not None:
        # Customize the response format to match our API
        custom_response = {
            'success': False,
            'message': response.data.get('detail', 'An error occurred'),
        }
        
        # Add any additional error details
        if isinstance(response.data, dict):
            errors = {k: v for k, v in response.data.items() if k != 'detail'}
            if errors:
                custom_response['errors'] = errors
        
        response.data = custom_response
    
    return response

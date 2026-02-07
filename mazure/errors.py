"""Azure API error response simulation."""

from typing import Dict, Any, Optional
import random
import time
from datetime import datetime


class AzureErrorSimulator:
    """Simulate realistic Azure API errors."""
    
    @staticmethod
    def throttling_error(retry_after_seconds: int = 60) -> Dict[str, Any]:
        """Generate 429 throttling error.
        
        Args:
            retry_after_seconds: Seconds to wait before retry
        
        Returns:
            Azure throttling error response
        """
        return {
            'error': {
                'code': 'TooManyRequests',
                'message': 'The request has been throttled. Retry after the specified time.',
                'details': [{
                    'code': 'TooManyRequests',
                    'message': f'Rate limit exceeded. Retry after {retry_after_seconds} seconds.'
                }]
            },
            '_status_code': 429,
            '_headers': {
                'Retry-After': str(retry_after_seconds),
                'x-ms-ratelimit-remaining': '0'
            }
        }
    
    @staticmethod
    def resource_not_found(resource_id: str) -> Dict[str, Any]:
        """Generate 404 not found error.
        
        Args:
            resource_id: Resource identifier
        
        Returns:
            Azure not found error response
        """
        return {
            'error': {
                'code': 'ResourceNotFound',
                'message': f'The Resource \'{resource_id}\' under resource group was not found.',
                'details': []
            },
            '_status_code': 404
        }
    
    @staticmethod
    def invalid_request(message: str) -> Dict[str, Any]:
        """Generate 400 bad request error.
        
        Args:
            message: Error message
        
        Returns:
            Azure bad request error response
        """
        return {
            'error': {
                'code': 'InvalidRequestContent',
                'message': message,
                'details': []
            },
            '_status_code': 400
        }
    
    @staticmethod
    def conflict_error(resource_id: str) -> Dict[str, Any]:
        """Generate 409 conflict error.
        
        Args:
            resource_id: Resource identifier
        
        Returns:
            Azure conflict error response
        """
        return {
            'error': {
                'code': 'ResourceExists',
                'message': f'The resource \'{resource_id}\' already exists.',
                'details': []
            },
            '_status_code': 409
        }
    
    @staticmethod
    def authorization_failed() -> Dict[str, Any]:
        """Generate 403 authorization error.
        
        Returns:
            Azure authorization error response
        """
        return {
            'error': {
                'code': 'AuthorizationFailed',
                'message': 'The client does not have authorization to perform action.',
                'details': []
            },
            '_status_code': 403
        }
    
    @staticmethod
    def internal_server_error() -> Dict[str, Any]:
        """Generate 500 internal server error.
        
        Returns:
            Azure internal error response
        """
        return {
            'error': {
                'code': 'InternalServerError',
                'message': 'The server encountered an internal error. Please retry the request.',
                'details': []
            },
            '_status_code': 500
        }
    
    @staticmethod
    def should_fail(failure_rate: float = 0.01) -> bool:
        """Randomly determine if request should fail.
        
        Args:
            failure_rate: Probability of failure (0.01 = 1%)
        
        Returns:
            True if should fail
        """
        return random.random() < failure_rate

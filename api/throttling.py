"""
Custom throttling classes for the Fitness Backend API.

Provides different rate limiting strategies for various API endpoints
to prevent abuse and ensure fair usage.

All throttles use IP-based rate limiting for consistent tracking.
"""

from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle


class AuthTokenRateThrottle(SimpleRateThrottle):
    """
    Strict rate limiting for authentication token endpoint.
    5 requests per minute per IP to prevent brute force attacks.
    """
    scope = 'auth_token'
    
    def get_cache_key(self, request, view):
        # IP-based throttling only
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }


class BurstRateThrottle(AnonRateThrottle):
    """
    Burst rate limiting for general API endpoints.
    Allows short bursts of requests but limits sustained usage.
    60 requests per minute per IP.
    """
    scope = 'burst'


class SustainedRateThrottle(AnonRateThrottle):
    """
    Sustained rate limiting for general API endpoints.
    Limits long-term usage.
    1000 requests per hour per IP.
    """
    scope = 'sustained'


class DataModificationRateThrottle(SimpleRateThrottle):
    """
    Rate limiting for data modification operations (POST/PUT/PATCH).
    30 requests per minute per IP to prevent spam and abuse.
    """
    scope = 'data_modification'
    
    def get_cache_key(self, request, view):
        # IP-based throttling only
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }


class ContentListingRateThrottle(SimpleRateThrottle):
    """
    Rate limiting for content listing and discovery endpoints.
    30 requests per minute per IP to prevent scraping.
    Used for: home feeds, shorts, trainer listings, playlist listings, etc.
    """
    scope = 'content_listing'
    
    def get_cache_key(self, request, view):
        # IP-based throttling only
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }


class SearchRateThrottle(SimpleRateThrottle):
    """
    Rate limiting for search query endpoints.
    20 requests per minute per IP to prevent abuse and scraping.
    Stricter than content listing due to expensive search operations.
    """
    scope = 'search'
    
    def get_cache_key(self, request, view):
        # IP-based throttling only
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }


class AdminActionRateThrottle(SimpleRateThrottle):
    """
    Rate limiting for admin actions.
    100 requests per hour per IP for admin operations.
    """
    scope = 'admin'
    
    def get_cache_key(self, request, view):
        # IP-based throttling only
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }

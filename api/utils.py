"""
Shared utility functions.

Provides consistent JSON response helpers, Redis cache wrappers,
and pagination utilities used across all API views.
"""
import os
from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse


CACHE_TTL = getattr(settings, "CACHE_TTL", 300)  # Default 5 minutes


# ---------------------------------------------------------------------------
# Pagination helpers
# ---------------------------------------------------------------------------

def pagination_params(request) -> tuple:
    """
    Parse and validate ?page and ?page_size query params.

    Returns:
        (page, page_size) tuple on success.
        Raises ValueError if params are invalid.
    """
    try:
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))
    except (ValueError, TypeError):
        raise ValueError("page and page_size must be integers")

    if page < 1:
        raise ValueError("page must be >= 1")
    if not (1 <= page_size <= 100):
        raise ValueError("page_size must be between 1 and 100")

    return page, page_size


def paginated_response(items: list, *, total: int, page: int, page_size: int) -> dict:
    """
    Build a pagination metadata dict suitable for passing to success_response().

    Args:
        items:      Serialized list of items for the current page.
        total:      Total number of items across all pages.
        page:       Current page number (1-based).
        page_size:  Number of items per page.

    Returns:
        Dict with "pagination" metadata and "results" list.

    Usage:
        page, page_size = pagination_params(request)
        qs = MyModel.objects.filter(is_active=True)
        total = qs.count()
        data = MySerializer(qs[(page-1)*page_size : page*page_size], many=True).data
        return success_response("OK", data=paginated_response(data, total=total, page=page, page_size=page_size))
    """
    import math
    total_pages = math.ceil(total / page_size) if page_size > 0 else 1
    return {
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_items": total,
            "page_size": page_size,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        },
        "results": items,
    }


# ---------------------------------------------------------------------------
# JSON Response helpers
# ---------------------------------------------------------------------------

def success_response(message: str, data=None, status: int = 200) -> JsonResponse:
    """
    Standard success response.

    Returns:
        { "success": true, "message": "...", "data": {...} }
    """
    response = {"success": True, "message": message}
    if data is not None:
        response["data"] = data
    return JsonResponse(response, status=status)


def error_response(message: str, status: int = 400, errors=None) -> JsonResponse:
    """
    Standard error response.

    Returns:
        { "success": false, "message": "...", "errors": {...} }
    """
    response = {"success": False, "message": message}
    if errors is not None:
        response["errors"] = errors
    return JsonResponse(response, status=status)


# ---------------------------------------------------------------------------
# Redis cache helpers
# ---------------------------------------------------------------------------

def set_cache(key: str, data, timeout: int = None) -> bool:
    """Store data in Redis cache. Returns True on success, False on error."""
    try:
        cache.set(key, data, timeout=timeout if timeout is not None else CACHE_TTL)
        return True
    except Exception as e:
        print(f"[Redis] set_cache error for key={key}: {e}")
        return False


def get_cache(key: str):
    """Retrieve data from Redis cache. Returns None on miss or error."""
    try:
        return cache.get(key)
    except Exception as e:
        print(f"[Redis] get_cache error for key={key}: {e}")
        return None


def delete_cache(key: str) -> bool:
    """Delete a key from Redis cache. Returns True on success, False on error."""
    try:
        cache.delete(key)
        return True
    except Exception as e:
        print(f"[Redis] delete_cache error for key={key}: {e}")
        return False

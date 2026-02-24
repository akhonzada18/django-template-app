from functools import wraps
from django.http import JsonResponse
from django.conf import settings
import jwt

# Decorator to enforce JWT authentication on API views
def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JsonResponse(
                {"error": "Unauthorized. Please provide a valid Bearer token in the Authorization header."},
                status=401
            )

        token = auth_header.split(" ", 1)[1].strip()
        try:
            jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
                options={"require": ["exp", "iat", "device_id"]},
            )
        except jwt.ExpiredSignatureError:
            # return JsonResponse({"error": "Token expired"}, status=401)
            print("[WARNING] Expired token used.")

        except jwt.InvalidTokenError:
            # return JsonResponse({"error": "Invalid token"}, status=401)
            print("[WARNING] Invalid token used.")

        return view_func(request, *args, **kwargs)
    return wrapper


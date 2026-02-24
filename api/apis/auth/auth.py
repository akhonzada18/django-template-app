import json, jwt, uuid
from datetime import datetime, timezone
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

from .helpers import b64_hmac_sha256, compare_signatures, is_fresh_timestamp, consume_nonce_once, validate_client_fields, store_refresh_token, is_refresh_token_valid, revoke_refresh_token
from .decorator import jwt_required
from ...utils import success_response, error_response
from ...throttling import AuthTokenRateThrottle


# Get JWT token for app authentication
@extend_schema(
    tags=['Authentication'],
    summary='Get JWT token',
    description='''Obtain a JWT token using HMAC-based authentication.
    
**How to use:**
1. Generate a unique nonce (UUID format)
2. Get current Unix timestamp (seconds since epoch)
3. Create signature string: `{device_id}/{timestamp}/{nonce}`
4. Compute HMAC-SHA256 with your secret key
5. Base64 encode the HMAC result
6. Send all fields in the request body

**Rate Limit:** 5 requests per minute (strict security limit)

**Note:** This endpoint does not require authorization header.''',
    auth=[],
    request={
        'application/json': {
            'example': {
            "device_id": "TEST-DEVICE-12345",
            "timestamp": "1735699900",
            "nonce": "2b0f6f5e-3b60-4d85-9e5f-9e9d8e1f8a44",
            "hmac_hash": "+cCJfeRtg05l0sxiV3PdMJmxuk4Woy6X462PSZ9najk="
            }

        }
    },
    responses={
        200: inline_serializer(
            name='TokenResponse',
            fields={
                'token': serializers.CharField(),
            }
        ),
    }
)
@method_decorator(csrf_exempt, name='dispatch')
class GetJWTTokenView(APIView):
    permission_classes = [AllowAny]  # No authentication required for getting token
    throttle_classes = [AuthTokenRateThrottle]  # Strict rate limiting: 5 requests per minute
    
    """
    Client POSTs JSON:
    {
      "device_id": "device123",
      "timestamp": "<epoch_seconds>",
      "nonce": "<uuid>",
      "hmac_hash": "<base64_signature>"
    }

    String to sign (ASCII):
      "{device_id}/{timestamp}/{nonce}"
    """
    
    def post(self, request):
        data = request.data
        if not isinstance(data, dict):
            return error_response("Invalid JSON", status=400)

        device_id = (data.get("device_id") or "").strip()
        ts        = str((data.get("timestamp") or "").strip())
        nonce     = (data.get("nonce") or "").strip()
        client_sig = (data.get("hmac_hash") or "").strip()

        # Validate payload fields
        if not device_id or not ts or not nonce or not client_sig:
            return error_response("Missing fields", status=400)

        if not validate_client_fields(device_id, ts, nonce, client_sig):
            return error_response("Invalid fields", status=400)

        # 1) Check timestamp
        if not is_fresh_timestamp(ts):
            print("Stale or invalid timestamp!")
            return error_response("Stale or invalid timestamp", status=422)

        # 2) Check nonce uniqueness
        if not consume_nonce_once(nonce, device_id):
            print("Replay detected!")
            return error_response("Replay detected", status=422)

        # 3) Recompute server signature
        string_to_sign = f"{device_id}/{ts}/{nonce}"
        server_sig = b64_hmac_sha256(settings.HMAC_SHARED_SECRET, string_to_sign)

        # 4) Constant-time compare
        if not compare_signatures(server_sig, client_sig):
            print("Invalid HMAC!")
            return error_response("Invalid HMAC", status=422)

        # 5) Issue JWT Access Token
        now = datetime.now(timezone.utc)
        access_payload = {
            "iat": int(now.timestamp()),
            "exp": int((now + settings.JWT_ACCESS_TTL).timestamp()),
            "device_id": device_id,
            "type": "access"
        }
        access_token = jwt.encode(access_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

        # 6) Issue JWT Refresh Token
        refresh_jti = str(uuid.uuid4())
        refresh_payload = {
            "iat": int(now.timestamp()),
            "exp": int((now + settings.JWT_REFRESH_TTL).timestamp()),
            "device_id": device_id,
            "jti": refresh_jti,
            "type": "refresh"
        }
        refresh_token = jwt.encode(refresh_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        
        # Store refresh token JTI
        store_refresh_token(device_id, refresh_jti)

        return JsonResponse({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": int(settings.JWT_ACCESS_TTL.total_seconds())
        }, status=200)


# Check authentication
@extend_schema(
    tags=['Authentication'],
    summary='Verify authentication',
    description='''Test if your JWT token is valid.
    
**How to use:**
1. Get your token from the `/auth/token` endpoint
2. Click the "Authorize" button (🔓) at the top of this page
3. Paste your token and click "Authorize"
4. Now you can test this endpoint

**Note:** Requires valid JWT token in Authorization header.''',
    responses={
        200: inline_serializer(
            name='AuthCheckResponse',
            fields={
                'success': serializers.BooleanField(),
                'message': serializers.CharField(),
            }
        ),
    }
)
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(jwt_required, name='dispatch')
class CheckAuthView(APIView):
    throttle_classes = [AuthTokenRateThrottle]  # Rate limit: 5 requests per minute
    
    def get(self, request):
        return success_response("Hello, you are authenticated!")


# Refresh JWT token
@extend_schema(
    tags=['Authentication'],
    summary='Refresh JWT token',
    description='''Get a new access token using your refresh token.
    
**How to use:**
1. Use your refresh token from the initial authentication
2. Send it in the request body
3. Receive a new access token

**Rate Limit:** 10 requests per minute

**Note:** This endpoint does not require authorization header.''',
    auth=[],
    request={
        'application/json': {
            'example': {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    },
    responses={
        200: inline_serializer(
            name='RefreshTokenResponse',
            fields={
                'access_token': serializers.CharField(),
                'token_type': serializers.CharField(),
                'expires_in': serializers.IntegerField(),
            }
        ),
    }
)
@method_decorator(csrf_exempt, name='dispatch')
class RefreshJWTTokenView(APIView):
    permission_classes = [AllowAny]  # No authentication required for refresh
    throttle_classes = [AuthTokenRateThrottle]  # Rate limit: 5 requests per minute
    
    """
    Client POSTs JSON:
    {
      "refresh_token": "<jwt_refresh_token>"
    }
    
    Returns new access token if refresh token is valid.
    """
    
    def post(self, request):
        data = request.data
        if not isinstance(data, dict):
            return error_response("Invalid JSON", status=400)

        refresh_token = (data.get("refresh_token") or "").strip()
        
        if not refresh_token:
            return error_response("Missing refresh_token", status=400)

        try:
            # Decode and validate refresh token
            payload = jwt.decode(
                refresh_token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
                options={"require": ["exp", "iat", "device_id", "jti", "type"]}
            )
            
            # Verify it's a refresh token
            if payload.get("type") != "refresh":
                return error_response("Invalid token type", status=422)
            
            device_id = payload.get("device_id")
            token_jti = payload.get("jti")
            
            # Check if refresh token is still valid (not revoked)
            if not is_refresh_token_valid(device_id, token_jti):
                return error_response("Refresh token revoked or invalid", status=401)
            
            # Issue new access token
            now = datetime.now(timezone.utc)
            access_payload = {
                "iat": int(now.timestamp()),
                "exp": int((now + settings.JWT_ACCESS_TTL).timestamp()),
                "device_id": device_id,
                "type": "access"
            }
            access_token = jwt.encode(access_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
            
            return JsonResponse({
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": int(settings.JWT_ACCESS_TTL.total_seconds())
            }, status=200)
            
        except jwt.ExpiredSignatureError:
            return error_response("Refresh token expired", status=401)
        except jwt.InvalidTokenError as e:
            return error_response(f"Invalid refresh token: {str(e)}", status=401)
        except Exception as e:
            return error_response(f"Error processing refresh token: {str(e)}", status=500)


import re
import hmac, hashlib, base64, time

from django.conf import settings
from ...utils import set_cache


# Strict Base64 regex
_BASE64_RE = re.compile(
    r"^(?:[A-Za-z0-9+/]{4})*"        # groups of 4 valid chars
    r"(?:[A-Za-z0-9+/]{2}==|"        # or 2 chars + '=='
    r"[A-Za-z0-9+/]{3}=)?$"          # or 3 chars + '='
)

# HMAC-SHA256 with Base64 encoding
def b64_hmac_sha256(secret: str, msg: str) -> str:
    digest = hmac.new(secret.encode("ascii"), msg.encode("ascii"), hashlib.sha256).digest()
    return base64.b64encode(digest).decode("ascii")

# Compare HMAC signatures
def compare_signatures(a: str, b: str) -> bool:
    # Normalize to ASCII bytes
    try:
        return hmac.compare_digest(a.encode("ascii"), b.encode("ascii"))
    except UnicodeEncodeError:
        return False

# Check if timestamp is within allowed drift
def is_fresh_timestamp(ts: str) -> bool:
    try:
        ts = int(ts)
    except ValueError:
        return False
    now = int(time.time())
    return abs(now - ts) <= settings.HMAC_ALLOWED_DRIFT_SECONDS

# Store nonce to prevent replay attacks
def consume_nonce_once(nonce: str, device_id: str) -> bool:
    """
    Returns True if nonce was not used before (stores it in cache), False if replayed.
    """
    key = f"hmac_nonce:{nonce}"
    value = f"device:{device_id}"

    return set_cache(key, value, settings.HMAC_NONCE_TTL_SECONDS)

# Validate client-supplied fields(payload)
def validate_client_fields(device_id: str, ts: str, nonce: str, sig: str) -> bool:
    """
    Basic sanity checks on client-supplied fields
    .
    Length limits, Base64 format, timestamp range.
    4 <= device_id <= 128 chars
    16 <= nonce <= 64 chars
    16 <= sig <= 64 chars (Base64)
    1735689600 <= ts <= 4793846400  (2025-01-01 .. 2125-01-01)
    """
    if not (4 <= len(device_id) <= 128):
        print("Invalid device_id length:", len(device_id))
        print("Device length should be between 4 and 128 characters.")
        return False
    if not (16 <= len(nonce) <= 64):
        print("Invalid nonce length:", len(nonce))
        print("Nonce length should be between 16 and 64 characters.")
        return False
    if not _BASE64_RE.match(sig):
        print("Invalid sig format:", sig)
        print("Signature must be a valid Base64 string.")
        return False
    try:
        ts_int = int(ts)
        # Reject far-future/ancient timestamps (basic sanity)
        if ts_int < 1735689600 or ts_int > 4793846400:  # (2025-01-01 to 2125-01-01)
            print("Timestamp out of range:", ts_int)
            print("Timestamp must be between 1735689600 and 4793846400 which is time between 2025-01-01 to 2125-01-01.")
            return False
    except ValueError:
        print("Invalid timestamp format:", ts)
        print("Timestamp must be an integer representing epoch seconds.")
        return False
    return True

# Store refresh token to track active sessions
def store_refresh_token(device_id: str, token_jti: str) -> bool:
    """
    Stores the refresh token JTI (JWT ID) for the device.
    Returns True if stored successfully.
    """
    key = f"refresh_token:{device_id}"
    return set_cache(key, token_jti, settings.JWT_REFRESH_TTL.total_seconds())

# Check if refresh token is valid and not revoked
def is_refresh_token_valid(device_id: str, token_jti: str) -> bool:
    """
    Validates if the refresh token JTI matches the stored one for the device.
    Returns True if valid, False if revoked or mismatched.
    """
    from ...utils import get_cache
    key = f"refresh_token:{device_id}"
    stored_jti = get_cache(key)
    return stored_jti == token_jti if stored_jti else False

# Revoke refresh token
def revoke_refresh_token(device_id: str) -> bool:
    """
    Revokes the refresh token for a device by removing it from cache.
    Returns True if successfully revoked.
    """
    from ...utils import delete_cache
    key = f"refresh_token:{device_id}"
    return delete_cache(key)

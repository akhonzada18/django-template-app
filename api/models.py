# Django imports
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


# ---------------------------------------------------------------------------
# BOILERPLATE MODELS — keep these in every project
# ---------------------------------------------------------------------------

class User(AbstractUser):
    """
    Custom user model extending Django AbstractUser.
    Uses username for authentication (Django default).
    Used for Django admin/CMS access and system authentication.
    """
    # Override email to make it required and unique
    email = models.EmailField(
        _("email address"),
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )

    # Additional profile fields
    title = models.CharField(max_length=10, blank=True, null=True)
    dob = models.DateField(_("date of birth"), blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)

    # Soft delete support
    deleted_at = models.DateTimeField(blank=True, null=True)

    REQUIRED_FIELDS = ["email"]

    class Meta:
        db_table = "users"
        verbose_name = _("user")
        verbose_name_plural = _("users")
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_staff"]),
        ]

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """
    App-level identity. One profile can own multiple devices.
    Used for personalization, history, content preferences, etc.
    """
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, db_index=True)
    avatar_url = models.URLField(max_length=500, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False, db_index=True)

    # Extensible metadata — store any extra per-profile data here
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_profiles"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["is_verified"]),
        ]

    def __str__(self):
        return self.email or self.name or str(self.id)


class Device(models.Model):
    """
    Physical device belonging to one user profile.
    The device_id is the primary auth identifier (used in HMAC/JWT flow).
    """
    device_id = models.CharField(max_length=200, unique=True, db_index=True)
    device_type = models.CharField(max_length=200, blank=True, null=True)
    app_version = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=50, null=True, blank=True)

    profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="devices",
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "devices"
        indexes = [
            models.Index(fields=["device_id"]),
            models.Index(fields=["profile"]),
        ]

    def __str__(self):
        return self.device_id


# ---------------------------------------------------------------------------
# PROJECT-SPECIFIC MODELS — add yours below
# ---------------------------------------------------------------------------



from rest_framework import serializers
from api.models import Device, UserProfile


class DeviceRegistrationSerializer(serializers.Serializer):
    """Validates the payload for registering a new device."""
    device_id = serializers.CharField(max_length=200)
    device_type = serializers.CharField(max_length=200, required=False, allow_blank=True)
    app_version = serializers.CharField(max_length=100, required=False, allow_blank=True)
    region = serializers.CharField(max_length=50, required=False, allow_blank=True)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["id", "name", "email", "avatar_url", "is_verified", "metadata", "created_at"]


class DeviceSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = Device
        fields = ["id", "device_id", "device_type", "app_version", "region", "profile", "created_at"]


# ---------------------------------------------------------------------------
# TODO: Add your project-specific serializers below, e.g.:
# ---------------------------------------------------------------------------
# from api.models import Category, Item
#
# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ["id", "title", "thumbnail_url", "is_active"]
#
# class ItemSerializer(serializers.ModelSerializer):
#     category = CategorySerializer(read_only=True)
#     class Meta:
#         model = Item
#         fields = ["id", "title", "description", "thumbnail_url", "category", "created_at"]

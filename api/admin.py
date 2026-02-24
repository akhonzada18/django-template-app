from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, Device


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "is_staff", "is_active", "date_joined")
    search_fields = ("username", "email")
    list_filter = ("is_staff", "is_active")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "name", "is_verified", "created_at")
    search_fields = ("email", "name")
    list_filter = ("is_verified",)


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("device_id", "device_type", "app_version", "region", "profile", "created_at")
    search_fields = ("device_id",)

# TODO: Register your project-specific models here, e.g.:
# from .models import Category, Item
#
# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ("id", "title", "is_active", "created_at")
#     search_fields = ("title",)
#     list_filter = ("is_active",)
#
# @admin.register(Item)
# class ItemAdmin(admin.ModelAdmin):
#     list_display = ("id", "title", "category", "is_active", "created_at")
#     search_fields = ("title",)
#     list_filter = ("is_active", "category")

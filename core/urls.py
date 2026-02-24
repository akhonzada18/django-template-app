"""
URL configuration for core project.
"""
import os

from api import views
from api.health import HealthCheckView, ReadinessCheckView, LivenessCheckView
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# API docs served under a secret token URL to prevent enumeration.
# TODO: Change this token before deploying to production.
API_DOCS_TOKEN = os.getenv("API_DOCS_TOKEN", "change-me-before-deploy")

urlpatterns = [
    path("admin/", admin.site.urls),

    # Health Check and Monitoring Endpoints (Kubernetes / load-balancer probes)
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("health/ready/", ReadinessCheckView.as_view(), name="readiness-check"),
    path("health/live/", LivenessCheckView.as_view(), name="liveness-check"),

    # API Documentation (obfuscated URL - set API_DOCS_TOKEN env var)
    path(f"api/{API_DOCS_TOKEN}/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(f"api/{API_DOCS_TOKEN}/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path(f"api/{API_DOCS_TOKEN}/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # CMS Authentication
    path("", views.dashboard_view, name="dashboard"),
    path("sign_in/", views.signin_view, name="sign_in"),
    path("logout/", views.Logout, name="log_out"),

    # CMS User Management
    path("users/", views.user_list_view, name="userList"),
    path("user/add/", views.add_user_view, name="addUser"),
    path("user/update/<int:id>/", views.update_user_view, name="updateUser"),
    path("user/restore/<int:id>/", views.restore_user_view, name="restoreUser"),
    path("user/delete/<int:id>/", views.delete_user_view, name="deleteUser"),

    # TODO: Add your project-specific CMS routes here, e.g.:
    # path("items/", views.item_list_view, name="itemList"),
    # path("item/<int:pk>/update/", views.item_update_view, name="itemUpdate"),

    # App API URL configurations
    path("api/v1/", include("api.urls")),
]

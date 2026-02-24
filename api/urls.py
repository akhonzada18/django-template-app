from django.urls import path, include

urlpatterns = [
    # Device onboarding (register a device - first call on app launch)
    path("", include("api.apis.onboarding.urls")),

    # Authentication (HMAC + JWT token exchange)
    path("auth/", include("api.apis.auth.urls")),

    # TODO: Add your project-specific API routes here, e.g.:
    # path("example/", include("api.apis.example.urls")),
]

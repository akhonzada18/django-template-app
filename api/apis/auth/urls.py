from django.urls import path
from .auth import GetJWTTokenView, CheckAuthView, RefreshJWTTokenView

urlpatterns = [
    path("get-token/", GetJWTTokenView.as_view()),
    path("refresh-token/", RefreshJWTTokenView.as_view()),
    path("check/", CheckAuthView.as_view()),
]

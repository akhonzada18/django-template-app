from django.urls import path
from .device import RegisterDeviceView

urlpatterns = [
    path("device/register/", RegisterDeviceView.as_view(), name="register_device"),
]

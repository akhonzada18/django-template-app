from django.urls import path
from .example import ExampleListView, ExampleDetailView

urlpatterns = [
    path("", ExampleListView.as_view(), name="example-list"),
    path("<int:pk>/", ExampleDetailView.as_view(), name="example-detail"),
]

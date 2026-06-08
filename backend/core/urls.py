from django.urls import path
from .views import api_hello

urlpatterns = [
    path("api/hello/", api_hello, name="api_hello"),
]

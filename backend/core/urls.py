from django.urls import path
from .views import api_hello, statsig_application

urlpatterns = [
    path("api/hello/", api_hello, name="api_hello"),
    path("statsig/application/", statsig_application, name="statsig_application"),
]

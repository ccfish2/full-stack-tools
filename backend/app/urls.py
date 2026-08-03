from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from core.views import index
import django_eventstream

urlpatterns = [
    path("", index),
    path("admin/", admin.site.urls),
    path("api_auth/", include("rest_framework.urls")),
    path("api/events/", django_eventstream.views.events, {"channels": ["global"]}),
    path("__reload__/", include("django_browser_reload.urls")),

    # include router URLs
    path("api/v1/", include(("core.api.v1.urls","core"), namespace= "v1")),
    path("api/v2/", include(("core.api.v2.urls", "core"), namespace="v2")),
]
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from core.views import StatsigViewSet

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("api_auth/", include("rest_framework.urls"))
]

router = DefaultRouter(trailing_slash=False)
router.register('statsig', StatsigViewSet)
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from core.views import StatsigViewSet, SSEEventViewSet, hello
import django_eventstream

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api_auth/", include("rest_framework.urls")),
    path("api/events/", django_eventstream.views.events, {"channels": ["global"]}),
    path("api/hello/", hello),
]

router = DefaultRouter(trailing_slash=False)
router.register('statsig', StatsigViewSet, basename="statsig")
router.register('trigger-events', SSEEventViewSet, basename="trigger-events")

urlpatterns += router.urls
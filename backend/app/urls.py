from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from core.views import StatsigViewSet, hello
import django_eventstream

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api_auth/", include("rest_framework.urls")),
    path("api/event", django_eventstream.views.events, {"channels":["global"]}),
    path("api/hello/", hello),
]

router = DefaultRouter(trailing_slash=False)
router.register('statsig', StatsigViewSet, basename="statsig")

urlpatterns += router.urls
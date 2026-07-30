from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from core.views import StatsigViewSet, SSEEventViewSet, hello, email_notification, index
import django_eventstream

router = DefaultRouter(trailing_slash=False)

router.register(r"statsigfeatureflag", 
                StatsigViewSet, 
                basename="statsigfeatureflag")

router.register(r"trigger-events", 
                SSEEventViewSet, 
                basename="trigger-events")

urlpatterns = [
    path("", index),
    path("admin/", admin.site.urls),
    path("api_auth/", include("rest_framework.urls")),
    path("api/events/", django_eventstream.views.events, {"channels": ["global"]}),
    path("api/hello/", hello),
    path("api/publishmsg/", email_notification),
    path("__reload__/", include("django_browser_reload.urls")),

    # include router URLs
    path("api/", include(router.urls)),
]
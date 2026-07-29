from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from core.views import StatsigViewSet, SSEEventViewSet, hello, email_notification
import django_eventstream

router = DefaultRouter(trailing_slash=False)

router.register(r"statsigfeatureflag", 
                StatsigViewSet, 
                basename="statsigfeatureflag")

router.register(r"trigger-events", 
                SSEEventViewSet, 
                basename="trigger-events")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api_auth/", include("rest_framework.urls")),
    path("api/events/", django_eventstream.views.events, {"channels": ["global"]}),
    path("api/hello/", hello),
    path("api/publishmsg/", email_notification),

    # include router URLS 
    path("api", include(router.urls))
]
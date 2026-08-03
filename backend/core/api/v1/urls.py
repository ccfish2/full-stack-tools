from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from core.api.v1.views import StatsigViewSet, SSEEventViewSet, hello, email_notification
import django_eventstream

router = DefaultRouter(trailing_slash=False)

router.register(r"statsigfeatureflag", 
                StatsigViewSet, 
                basename="statsigfeatureflag")

router.register(r"trigger-events", 
                SSEEventViewSet, 
                basename="trigger-events")

urlpatterns = [
    path("hello/", hello),
    path("publishmsg/", email_notification),

    # include router URLs
    path("", include(router.urls)),
]
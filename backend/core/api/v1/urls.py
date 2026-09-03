from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from core.api.v1.views import StatsigViewSet, UserViewSet, SSEEventViewSet, hello, email_notification, current_user, create_user
import django_eventstream

router = DefaultRouter(trailing_slash=False)

router.register(r"statsigfeatureflag", 
                StatsigViewSet, 
                basename="statsigfeatureflag")

router.register(r"trigger-events", 
                SSEEventViewSet, 
                basename="trigger-events")

router.register(r"users", 
                UserViewSet, 
                basename="users")

urlpatterns = [
    path("hello/", hello),
    path("user/", current_user),
    path("users/", create_user),
    path("publishmsg/", email_notification),

    # include router URLs
    path("", include(router.urls)),
]
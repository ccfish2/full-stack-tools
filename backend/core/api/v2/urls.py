from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.api.v1.views import hello, email_notification, SSEEventViewSet
from core.api.v2.views import StatsigViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"statsigfeatureflag", StatsigViewSet, basename="statsigfeatureflag-v2")
router.register(r"trigger-events", SSEEventViewSet, basename="trigger-events-v2")

urlpatterns = [
    path("hello/", hello),
    path("publishmsg/", email_notification),
    path("", include(router.urls)),
]
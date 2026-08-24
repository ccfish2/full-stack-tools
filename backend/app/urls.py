from django.contrib import admin
from django.urls import include, path
import django_eventstream
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.api.v1.views import grant_user_token
from core.views import index

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


urlpatterns = [
    path("", index),
    path("admin/", admin.site.urls),
    path("api_auth/", include("rest_framework.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/grant/", grant_user_token, name="token_grant"),
    path("api/events/", django_eventstream.views.events, {"channels": ["global"]}),
    path("__reload__/", include("django_browser_reload.urls")),

    # include router URLs
    path("api/v1/", include(("core.api.v1.urls","core"), namespace= "v1")),
    path("api/v2/", include(("core.api.v2.urls", "core"), namespace="v2")),
]

# OpenAPI swagger doc and redoc
urlpatterns += [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    path("api/v1/schema/", SpectacularAPIView.as_view(custom_settings={"SCHEMA_PATH_PREFIX": r"/api/v1"}), name="schema-v1"),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema-v1"), name="swagger-ui-v1"),
    path("api/v1/redoc/", SpectacularRedocView.as_view(url_name="schema-v1"), name="redoc-v1"),

    path("api/v2/schema/", SpectacularAPIView.as_view(custom_settings={"SCHEMA_PATH_PREFIX": r"/api/v2"}), name="schema-v2"),
    path("api/v2/docs/", SpectacularSwaggerView.as_view(url_name="schema-v2"), name="swagger-ui-v2"),
    path("api/v2/redoc/", SpectacularRedocView.as_view(url_name="schema-v2"), name="redoc-v2"),
]
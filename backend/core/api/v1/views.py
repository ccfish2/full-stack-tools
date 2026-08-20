
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from datetime import timedelta

from core.api.v1.serializers import (
    StatsigSerializer,
    SSEEventSerializer,
    UserCreateSerializer,
    UserListSerializer,
)
from core.models import StatsigApplication, SSEEvent
from core.tasks import publish_sse_event, email_users
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, BasePermission, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class IsReadOnlyOrAdmin(BasePermission):
    """Allow authenticated reads; require staff privileges for mutations."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        if request.user.is_staff:
            return True
        token_operations = set((request.auth or {}).get("operations", []))
        return request.method in token_operations


@extend_schema(
    request={
        "type": "object",
        "properties": {
            "username": {"type": "string"},
            "operations": {
                "type": "array",
                "items": {"type": "string", "enum": ["POST", "PUT", "PATCH", "DELETE"]},
            },
            "duration": {"type": "string", "enum": ["24h", "1w", "1m", "1y"]},
        },
        "required": ["username", "operations", "duration"],
    },
    responses={200: {"type": "object"}},
)
@api_view(["POST"])
@permission_classes([IsAdminUser])
def grant_user_token(request):
    username = request.data.get("username")
    operations = request.data.get("operations", [])
    duration = request.data.get("duration")
    allowed_operations = {"POST", "PUT", "PATCH", "DELETE"}
    durations = {
        "24h": timedelta(hours=24),
        "1w": timedelta(weeks=1),
        "1m": timedelta(days=30),
        "1y": timedelta(days=365),
    }

    if not isinstance(operations, list) or not set(operations).issubset(allowed_operations):
        return Response({"detail": "operations must contain only POST, PUT, PATCH, DELETE."}, status=400)
    if duration not in durations:
        return Response({"detail": "duration must be 24h, 1w, 1m, or 1y."}, status=400)

    user = User.objects.filter(username=username).first()
    if user is None or not user.is_active:
        return Response({"detail": "Target user does not exist or is inactive."}, status=404)
    if user.is_staff:
        return Response({"detail": "Scoped grants are only for readonly users."}, status=400)

    token = AccessToken.for_user(user)
    token["operations"] = operations
    token.set_exp(lifetime=durations[duration])
    return Response({"access": str(token), "username": user.username, "operations": operations, "duration": duration})

@api_view(["GET"])
@permission_classes([AllowAny])
def hello(request):
    return Response({"message": "Hello from Django backend", "status": "ok"})

class SSEEventViewSet(viewsets.ModelViewSet):
    """
    POST /trigger-events  {"channel": "global", "event_type": "message", "payload": {...}}
    Persists the SSEEvent row (via the serializer, like any other ModelViewSet),
    then queues publish_sse_event on Celery. That task calls
    django_eventstream.send_event(), which pushes to Redis; any TypeScript
    client with an open EventSource on /api/events/?channel=<channel> pulls
    it from there via its onmessage handler.
    """
    serializer_class = SSEEventSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return SSEEvent.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save()
        publish_sse_event.delay(instance.channel, instance.event_type, instance.payload)

class StatsigViewSet(viewsets.ModelViewSet):
    """
    POST /api/v1/statsigfeatureflag post product, environment, checksum and associated feature into the system 
    GET /api/v1/statsigfeatureflag retrieving Statsig feature from the system
    """
    serializer_class = StatsigSerializer
    permission_classes = [IsReadOnlyOrAdmin]

    def get_queryset(self):
        return StatsigApplication.objects.all()

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    return Response({
        "id": request.user.id,
        "username": request.user.username,
        "email": request.user.email,
        "is_staff": request.user.is_staff,
        "is_superuser": request.user.is_superuser,
    })

@extend_schema(
    request=UserCreateSerializer,
    responses={200: UserListSerializer(many=True), 201: UserCreateSerializer},
)
@api_view(["GET", "POST"])
@permission_classes([IsAdminUser])
def create_user(request):
    if request.method == "GET":
        users = User.objects.all().order_by("username")
        return Response(UserListSerializer(users, many=True).data)

    serializer = UserCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
    }, status=201)

@api_view(["POST"])
@permission_classes([AllowAny])
def email_notification(request):
    task = email_users.enqueue(
        emails=["seniorsoftwareengineerleader@gmail.com"],
        subject="You have a message: use django6.0 task framework",
        message="please upgrade requirements to django6.0",
    )

    return Response({
        "status": "queued",
        "message": "Email task has been queued",
        "task_id": getattr(task, "id", None),
    })
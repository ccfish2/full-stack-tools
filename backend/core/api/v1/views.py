
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
from django.utils.dateparse import parse_datetime
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import (extend_schema,
                                   OpenApiParameter,
                                   OpenApiTypes,
                                   extend_schema_view)
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import action


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

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="environment",
                type=OpenApiTypes.STR,
                location = OpenApiParameter.QUERY,
                required=False,
                enum=["prod","stage","dev"],
                description="Filter feature flag through input environment"
            ),

            OpenApiParameter(
                            name="updated_at",
                            type=OpenApiTypes.DATETIME,
                            location = OpenApiParameter.QUERY,
                            required=False,
                            enum=["prod","stage","dev"],
                            description="Return records updated at or after this ISO-8601 timestamp."
                        ),
        ]
    )
)
class StatsigViewSet(viewsets.ModelViewSet):
    """
    POST /api/v1/statsigfeatureflag post product, environment, checksum and associated feature into the system 
    GET /api/v1/statsigfeatureflag retrieving Statsig feature from the system
    """
    serializer_class = StatsigSerializer
    permission_classes = [IsReadOnlyOrAdmin]

    def get_queryset(self):
        queryset=(
            StatsigApplication.objects
            .prefetch_related("snapshots")
            .order_by("-updated_at")
        )

        environment = self.request.query_params.get("environment")
        updated_at = self.request.query_params.get("updated_at")

        if environment:
            queryset = queryset.filter(environment=environment)

        if updated_at:
            parsed_updated_at=parse_datetime(updated_at)

            if parsed_updated_at is None:
                raise ValidationError({
                    "updated_at": "Use a valid ISO-8601 datetime"
                })
            queryset = queryset.filter(updated_at=parsed_updated_at)
        return queryset

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

from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from core.api.v1.serializers import UserCreateSerializer, UserListSerializer
from django.contrib.auth import get_user_model

User = get_user_model()
class UserViewSet(ViewSet):
    """
    /api/v1/users/           - list all users (GET), create user (POST)
    /api/v1/users/current/   - get current user (GET)
    """
    queryset = User.objects.all()  # ← Add this
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return UserCreateSerializer
        return UserListSerializer
    
    def list(self, request):
        """GET /users/ - List all users"""
        users = User.objects.all().order_by("username")
        serializer = self.get_serializer_class()(users, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """POST /users/ - Create a new user"""
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        }, status=201)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def current(self, request):
        """GET /users/current/ - Get current authenticated user"""
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
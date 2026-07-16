
from rest_framework import viewsets

from .serializers import StatsigSerializer, SSEEventSerializer
from .models import StatsigApplication, SSEEvent
from .tasks import publish_sse_event
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

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
    serializer_class = StatsigSerializer
   
    def get_queryset(self):
        return StatsigApplication.objects.all()
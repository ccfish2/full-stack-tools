
from rest_framework import viewsets

from .serializers import StatsigSerializer
from .models import StatsigApplication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(["GET"])
@permission_classes([AllowAny])
def hello(request):
    return Response({"message": "Hello from Django backend", "status": "ok"})

class StatsigViewSet(viewsets.ModelViewSet):
    serializer_class = StatsigSerializer
   
    def get_queryset(self):
        return StatsigApplication.objects.all()
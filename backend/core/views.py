
from rest_framework import viewsets

from backend.core.serializers import StatsigSerializer

class StatsigViewSet(viewsets.ModelViewSet):
    serializer_class = StatsigSerializer
   
    def get_queryset(self):
        return
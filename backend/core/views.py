
from rest_framework import viewsets

from .serializers import StatsigSerializer
from .models import StatsigApplication

class StatsigViewSet(viewsets.ModelViewSet):
    serializer_class = StatsigSerializer
   
    def get_queryset(self):
        return StatsigApplication.all.objects()
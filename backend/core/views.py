from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from serializers import StatsigSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from .models import StatsigApplication

def api_hello(request):
    return JsonResponse({
        "message": "Hello from Django backend",
        "status": "ok",
    })

class StatsigViewSet(viewsets.ViewSet):
    """
      mainly post
    """

    def list(self, request):
        pass

    def create(self, request):
        pass

    def retrieve(self, request, pk=None):
        pass

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass
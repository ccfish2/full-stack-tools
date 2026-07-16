from rest_framework import serializers
from .models import StatsigApplication, SSEEvent

class StatsigSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatsigApplication
        fields = ['id', 'data', 'updated_at', 'created_at']


class SSEEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SSEEvent
        fields = ['id', 'channel', 'event_type', 'payload', 'created_at']
        read_only_fields = ['id', 'created_at']
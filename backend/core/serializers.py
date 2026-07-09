from rest_framework import serializers
from .models import StatsigApplication

class StatsigSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatsigApplication
        fields = ['id', 'data', 'updated_at', 'created_at']
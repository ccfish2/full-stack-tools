from rest_framework import serializers
from models import StatsigApplication

class StatsigSerializer(serializers.Serializer):
    data = serializers.JSONField(max=5000)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def create(self, validated_data):
        return StatsigApplication(**validated_data)

    def update(self, instance, validated_data):
        instance.data = validated_data.get('data', instance.email)
        instance.created_at = validated_data.get('created_at', instance.content)
        instance.updated_at = validated_data.get('updated_at', instance.created)
        return instance
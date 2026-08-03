from rest_framework import serializers
from core.models import StatsigApplication, SSEEvent, StatsigMetadataSnapShots


class StatsigMetadataSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatsigMetadataSnapShots
        fields = [
            "id",
            "timestamp",
            "metadata",
        ]

class StatsigSerializer(serializers.ModelSerializer):
    snapshots = StatsigMetadataSnapshotSerializer(many=True, read_only=True)

    class Meta:
        model = StatsigApplication
        fields = [
            "id",
            "product",
            "environment",
            "last_checksum",
            "created_at",
            "updated_at",
            "snapshots",
        ]

class SSEEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SSEEvent
        fields = ['id', 'channel', 'event_type', 'payload', 'created_at']
        read_only_fields = ['id', 'created_at']
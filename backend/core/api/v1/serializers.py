from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import StatsigFeatures, SSEEvent, ProductStatsigSnapShots

User = get_user_model()

class ProductStatsigSnapShotserializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStatsigSnapShots
        fields = [
            "id",
            "timestamp",
            "productid",
            "productName",
            "featureflaglastchecksum",
            "statsig_flag",
        ]

class StatsigSerializer(serializers.ModelSerializer):
    snapshots = ProductStatsigSnapShotserializer(many=True, read_only=True)

    class Meta:
        model = StatsigFeatures
        fields = [
            "id",
            "environment",
            "checksum",
            "created_at",
            "updated_at",
            "metadata",
            "snapshots", 
        ]

class SSEEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SSEEvent
        fields = ['id', 'channel', 'event_type', 'payload', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=["admin", "readonly"], write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "role"]

    def create(self, validated_data):
        role = validated_data.pop("role")
        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.is_staff = role == "admin"
        user.is_superuser = role == "admin"
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "is_active", "is_staff", "is_superuser"]
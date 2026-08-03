from rest_framework import serializers

from core.api.v1.serializers import StatsigSerializer as StatsigSerializerV1

class StatsigSerializerV2(StatsigSerializerV1):
    class Meta(StatsigSerializerV1.Meta):
        pass  # diverge fields here when v2 actually needs to
from core.api.v1.views import StatsigViewSet as StatsigViewSetV1, hello, email_notification
from core.api.v1.views import SSEEventViewSet
from core.api.v2.serializers import StatsigSerializerV2


class StatsigViewSet(StatsigViewSetV1):
    serializer_class = StatsigSerializerV2
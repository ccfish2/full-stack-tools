
from core.models import ProductStatsigSnapShots
import django_filters


class ProductFilter(django_filters.FilterSet):
    updated_at = django_filters.DateFilter(field_name='updated_at__date')
    created_at = django_filters.DateFilter(field_name='created_at__date')

    class Meta:
        model = ProductStatsigSnapShots
        fields = {
            'productid': ['iexact', 'icontains'],
            'productName': ['iexact', 'icontains'],
        }

class ProductStatsigSnapshotFilter(django_filters.FilterSet):
    productid = django_filters.CharFilter(field_name='productid', lookup_expr='icontains')
    productName = django_filters.CharFilter(field_name='productName', lookup_expr='icontains')
    featureflaglastchecksum = django_filters.CharFilter(
        field_name='featureflaglastchecksum',
        lookup_expr='iexact',
    )
    timestamp = django_filters.DateTimeFromToRangeFilter(field_name='timestamp')

    class Meta:
        model = ProductStatsigSnapShots
        fields = ["productid", "productName", "timestamp", "featureflaglastchecksum"]

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
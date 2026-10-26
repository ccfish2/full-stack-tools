import os
import sys
from pathlib import Path
from pprint import pprint
import datetime
from datetime import timedelta
from django.utils import timezone
import django
from django.db import connection
from django.test.utils import CaptureQueriesContext

def run2():
    from core.models import ProductStatsigSnapShots, StatsigFeatures
    # features = StatsigFeatures.objects.filter(checksum='62f1374a4fff4756e3cb3d59447d55e06863569153b4a83bbf298b3e71133c75').delete()
    # pprint(features)
    # pprint(connection.queries)

    pprint("----***----")
    update = StatsigFeatures.objects.all().update(updated_at=timezone.now() - timedelta(days=20))
    pprint(update)
    pprint(connection.queries)

def run():
    from core.models import ProductStatsigSnapShots, StatsigFeatures
    Environment = StatsigFeatures.Environment

    with CaptureQueriesContext(connection) as queries:
        list(StatsigFeatures.objects.all())
    pprint(queries.captured_queries)
    pprint("Display product name")
    for e in ProductStatsigSnapShots.objects.all():
        pprint(e.productName)
        pprint(e.productid)
        pprint("----------")

    pprint("*********")
    pprint("Display product environment")
    all = StatsigFeatures.objects.all()
    filter = all.filter(environment='prod')
    sql, params = filter.query.sql_with_params()
    print("SQL:", sql)
    print("Parameters:", params)
    for e in filter:
        pprint(e.metadata)
        pprint("----------")

    pprint("*********")
    pprint("Exclude date time and environment")
    exclude = all.exclude(created_at__gt=datetime.date(2026, 9, 17)).exclude(environment='dev')
    for e in exclude:
        pprint(e.metadata)
        pprint(e.created_at)
        pprint("----------")


    pprint("*********")
    from django.db.models import Value, CharField
    annotated = all.annotate(
    number_of_entries=Value(
        Environment.STAGE,
        output_field=CharField(),
    )
)
    pprint(annotated.explain)
    pprint(annotated[0].number_of_entries)

if __name__ == "__main__":
    backend_dir = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(backend_dir))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
    django.setup()
    run2()
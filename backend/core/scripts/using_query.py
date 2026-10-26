import os
import sys
from pathlib import Path
from pprint import pprint
import datetime

import django
from django.db import connection
from django.test.utils import CaptureQueriesContext

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
    run()
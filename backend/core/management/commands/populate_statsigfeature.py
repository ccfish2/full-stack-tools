import hashlib
import json

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import ProductStatsigSnapShots, StatsigFeatures


class Command(BaseCommand):
    help = "Populate realistic Statsig feature flag data and snapshot records."

    def _checksum_for_metadata(self, metadata):
        normalized = json.dumps(metadata, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def handle(self, *args, **options):
        seed_records = [
            {
                "environment": "prod",
                "metadata": {
                    "environment": "prod",
                    "status": "approved",
                    "version": "v1",
                    "production": "product",
                    "rollout": 100,
                    "owner": "platform-team",
                    "release_channel": "stable",
                    "visibility": "internal",
                    "updated_by": "release-bot",
                },
                "products": [
                    {
                        "productid": "gpu_100",
                        "productName": "gpu model 100 speed 5x memory 5g",
                    },
                    {
                        "productid": "gpu_200",
                        "productName": "gpu model 200 speed 8x memory 10g",
                    },
                ],
            },
            {
                "environment": "stage",
                "metadata": {
                    "environment": "stage",
                    "status": "approved",
                    "version": "v2",
                    "production": "staging",
                    "rollout": 65,
                    "owner": "qa-team",
                    "release_channel": "beta",
                    "visibility": "customer-facing",
                    "updated_by": "qa-automation",
                },
                "products": [
                    {
                        "productid": "gpu_150",
                        "productName": "gpu model 150 speed 6x memory 7g",
                    },
                    {
                        "productid": "gpu_250",
                        "productName": "gpu model 250 speed 9x memory 12g",
                    },
                ],
            },
            {
                "environment": "dev",
                "metadata": {
                    "environment": "dev",
                    "status": "approved",
                    "version": "v3",
                    "production": "prototype",
                    "rollout": 25,
                    "owner": "engineering",
                    "release_channel": "dev",
                    "visibility": "internal",
                    "updated_by": "developer",
                },
                "products": [
                    {
                        "productid": "gpu_75",
                        "productName": "gpu model 75 speed 3x memory 4g",
                    },
                    {
                        "productid": "gpu_125",
                        "productName": "gpu model 125 speed 4x memory 6g",
                    },
                ],
            },
        ]

        created_statsig_count = 0
        created_snapshot_count = 0

        for record in seed_records:
            environment = record["environment"]
            metadata = record["metadata"]
            checksum = self._checksum_for_metadata(metadata)

            statsig_flag, created = StatsigFeatures.objects.update_or_create(
                environment=environment,
                checksum=checksum,
                defaults={
                    "metadata": metadata,
                },
            )

            if created:
                created_statsig_count += 1

            for product in record["products"]:
                snapshot, snapshot_created = ProductStatsigSnapShots.objects.get_or_create(
                    statsig_flag=statsig_flag,
                    productid=product["productid"],
                    defaults={
                        "productName": product["productName"],
                        "timestamp": timezone.now(),
                        "featureflaglastchecksum": checksum,
                    },
                )

                if snapshot_created:
                    created_snapshot_count += 1
                else:
                    snapshot.productName = product["productName"]
                    snapshot.timestamp = timezone.now()
                    snapshot.featureflaglastchecksum = checksum
                    snapshot.save(update_fields=["productName", "timestamp", "featureflaglastchecksum"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_statsig_count} StatsigFeatures rows and {created_snapshot_count} snapshot rows."
            )
        )

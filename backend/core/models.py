from django.db import models

class ExampleItem(models.Model):
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class StatsigApplication(models.Model):
    class Environment(models.TextChoices):
        PROD = "prod", "Production"
        STAGE = "stage", "Stage"
        DEV = "dev", "Development"
    last_checksum = models.CharField(max_length=256,default="") # the last snapshot of this product
    environment = models.CharField(
        max_length=10,
        choices=Environment.choices,
        default="stage"

    )
    product = models.CharField(max_length=100,default="stage") # which product this feature flag belongs to 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product} ({self.environment})"

class StatsigMetadataSnapShots(models.Model):
    statsig_flag = models.ForeignKey(
        StatsigApplication, 
        on_delete=models.CASCADE,
        related_name="snapshots",
    )
    timestamp = models.DateTimeField() # the created timestamp of this snapshots
    metadata = models.JSONField() # json blob of all metata

    def __str__(self):
        return f"{self.statsig_flag.product} @{self.timestamp}"

class SSEEvent(models.Model):
    """
    Every trigger is persisted here (via SSEEventViewSet.perform_create),
    then published to Redis/django-eventstream through the publish_sse_event
    Celery task, so there's an auditable log of what was sent over SSE.
    """
    channel = models.CharField(max_length=128, default="global")
    event_type = models.CharField(max_length=64, default="message")
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"SSEEvent({self.channel}, {self.event_type}) #{self.id}"

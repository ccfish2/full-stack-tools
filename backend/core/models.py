from django.db import models

class ExampleItem(models.Model):
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class StatsigFeatures(models.Model):
    class Environment(models.TextChoices):
        PROD = "prod", "Production"
        STAGE = "stage", "Stage"
        DEV = "dev", "Development"
    
    environment = models.CharField(
        max_length=10,
        choices=Environment.choices,
        default="stage"
    )
    name = models.CharField(max_length=256, default="", blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(default=dict, blank=False)  # Current state of feature flag data
    checksum = models.CharField(max_length=256, default="", blank=False)  # Hash of current metadata state

    class Meta:
        unique_together = ('environment', 'checksum')

    def __str__(self):
        return f"StatsigFeatures - {self.environment} (checksum: {self.checksum[:8]}...)"


class ProductStatsigSnapShots(models.Model):
    """
    Historical snapshots of which StatsigFeatures state each product had at a given time.
    Multiple products can reference the same feature flag state (checksum).
    """
    statsig_flag = models.ForeignKey(
        StatsigFeatures, 
        on_delete=models.CASCADE,
        related_name="snapshots",
    )
    productid = models.CharField(max_length=100, default="gpu_100")
    productName = models.CharField(max_length=500, default="gpu model 100 speed 5x memory 5g")
    timestamp = models.DateTimeField()  # When this product captured/received this feature flag snapshot
    featureflaglastchecksum = models.CharField(max_length=256, default="")  # Checksum of StatsigFeatures.metadata at this timestamp
    
    class Meta:
        indexes = [
            models.Index(fields=['featureflaglastchecksum']),
            models.Index(fields=['productid', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.productid} @ {self.timestamp}"

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

## wizard-feature
class Business(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Guest(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=12)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True)

    @property
    def full_name(self):
        return self.full_name

class Booking(models.Model):
    class RoomType(models.TextChoices):
        SINGLE="Single"
        DOUBLE="Double"
        FAMILY="Family"
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name="bookings")
    room_type = models.CharField(max_length=10, choices=RoomType.choices)
    date = models.DateField()
    number_of_night = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.guest.full_name}: {self.number_of_night} nights in {self.room_type} room"

## end of wizard-feature

from django.db import models
import json


class ExampleItem(models.Model):
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class StatsigApplication(models.Model):
    data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"StatsigApplication {self.id}"


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

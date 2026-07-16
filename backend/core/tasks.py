from celery import shared_task
from django_eventstream import send_event
import logging

logger = logging.getLogger(__name__)


@shared_task
def publish_sse_event(channel: str, event_type: str, payload: dict):
    """
    Runs in the Celery worker process, not the web process.
    Pushes an event into django-eventstream's Redis-backed storage;
    any client with an open SSE connection on `channel` receives it.
    """
    logger.info(f"publish_sse_event -> channel={channel} type={event_type} payload={payload}")
    send_event(channel, event_type, payload)
    return {"channel": channel, "event_type": event_type, "payload": payload}


@shared_task
def process_event(event_data):
    """
    Reads event details and processes them.
    Placeholder for now — will eventually publish to the SSE stream
    once django-eventstream is wired in (step 3).
    """
    logger.info(f"Processing event: {event_data}")

    # TODO: replace with real processing logic —
    # e.g. persist to DB, transform payload, validate schema, etc.
    processed = {
        "status": "processed",
        "original": event_data,
    }

    return processed

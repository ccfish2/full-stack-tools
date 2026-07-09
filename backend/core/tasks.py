from celery import shared_task
import logging

logger = logging.getLogger(__name__)
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

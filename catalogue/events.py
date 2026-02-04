from django.utils import timezone
from core.rabbitmq import publish_event


def publish_catalogue_event(resource: str, action: str, resource_id, payload: dict):
    event = {
        'resource': resource,
        'action': action,
        'id': resource_id,
        'timestamp': timezone.now().isoformat(),
        'payload': payload,
    }
    publish_event(f"catalogue.{resource}.{action}", event)

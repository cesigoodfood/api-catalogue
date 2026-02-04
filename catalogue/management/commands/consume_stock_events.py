import decimal
import json
import pika
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from core.rabbitmq import RABBITMQ_EXCHANGE
from catalogue.models import Product


class Command(BaseCommand):
    help = "Consume stock events"

    def handle(self, *args, **options):
        creds = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS)
        params = pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            credentials=creds,
        )
        conn = pika.BlockingConnection(params)
        ch = conn.channel()
        ch.exchange_declare(exchange=RABBITMQ_EXCHANGE, exchange_type="topic", durable=True)
        q = ch.queue_declare(queue="", exclusive=True)
        queue_name = q.method.queue
        ch.queue_bind(exchange=RABBITMQ_EXCHANGE, queue=queue_name, routing_key="stock.#")

        def callback(ch, method, properties, body):
            event = json.loads(body)
            resource = event.get("resource")
            action = event.get("action")
            payload = event.get("payload") or {}
            if resource != "products":
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            product_id = event.get("id") or payload.get("id")
            name = payload.get("name")
            restaurant_id = payload.get("restaurantId")

            if action in ("created", "updated"):
                if product_id is None or name is None or restaurant_id is None:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return

                in_stock = True
                base = getattr(settings, "STOCK_API_BASE", "").rstrip("/")
                if base:
                    try:
                        url = f"{base}/products/{product_id}/availability/"
                        resp = requests.get(url, timeout=2)
                        if resp.status_code == 200:
                            payload_av = resp.json()
                            in_stock = bool(payload_av.get("available"))
                    except Exception:
                        in_stock = True

                existing = Product.objects.filter(id=product_id).first()
                if existing is None:
                    Product.objects.create(
                        id=product_id,
                        name=name,
                        restaurant_id=restaurant_id,
                        description=None,
                        image_url=None,
                        price=decimal.Decimal("0.00"),
                        available=in_stock,
                        category=None,
                        deleted_at=None,
                    )
                else:
                    Product.objects.filter(id=product_id).update(
                        name=name,
                        restaurant_id=restaurant_id,
                        available=in_stock,
                        deleted_at=None,
                    )

            if action == "deleted":
                Product.objects.filter(id=product_id).update(deleted_at=timezone.now())

            ch.basic_ack(delivery_tag=method.delivery_tag)

        ch.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)
        ch.start_consuming()

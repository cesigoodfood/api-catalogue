import json
import os
import pika

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS", "guest")
RABBITMQ_EXCHANGE = os.environ.get("RABBITMQ_EXCHANGE", "goodfood.events")


def _connection():
    creds = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=creds)
    return pika.BlockingConnection(params)


def publish_event(routing_key: str, payload: dict):
    body = json.dumps(payload, default=str)
    conn = _connection()
    ch = conn.channel()
    ch.exchange_declare(exchange=RABBITMQ_EXCHANGE, exchange_type="topic", durable=True)
    ch.basic_publish(exchange=RABBITMQ_EXCHANGE, routing_key=routing_key, body=body)
    conn.close()

import decimal

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from catalogue.models import Product


class Command(BaseCommand):
    help = "Sync products from stock service into catalogue"

    def add_arguments(self, parser):
        parser.add_argument(
            "--restaurant-id",
            type=int,
            required=True,
            help="Restaurant ID to sync products for",
        )

    def handle(self, *args, **options):
        restaurant_id = options["restaurant_id"]
        base = getattr(settings, "STOCK_API_BASE", "").rstrip("/")
        if not base:
            self.stderr.write("STOCK_API_BASE is not configured.")
            return

        url = f"{base}/products/"
        params = {"restaurantId": restaurant_id}

        try:
            resp = requests.get(url, params=params, timeout=5)
        except requests.RequestException as exc:
            self.stderr.write(f"Stock API request failed: {exc}")
            return

        if resp.status_code != 200:
            self.stderr.write(f"Stock API returned {resp.status_code}: {resp.text}")
            return

        payload = resp.json()
        items = payload.get("results") if isinstance(payload, dict) else payload
        if not isinstance(items, list):
            self.stderr.write("Unexpected response format from Stock API.")
            return

        created = 0
        updated = 0
        for item in items:
            pid = item.get("id")
            name = item.get("name")
            rid = item.get("restaurantId")
            if pid is None or name is None or rid is None:
                continue
            obj, was_created = Product.objects.update_or_create(
                id=pid,
                defaults={
                    "name": name,
                    "restaurant_id": rid,
                    "description": None,
                    "image_url": None,
                    "price": decimal.Decimal("0.00"),
                    "available": True,
                    "category": None,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(f"Synced products for restaurant {restaurant_id}. Created: {created}, Updated: {updated}")

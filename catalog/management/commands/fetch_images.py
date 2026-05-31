import os
import random
import requests

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from catalog.models import Product
from catalog.management.commands.flower_keywords import FLOWER_KEYWORDS


class Command(BaseCommand):
    help = "Fetch product images from Pexels and save to product.image."

    def add_arguments(self, parser):
        parser.add_argument(
            "--api-key",
            default=None,
            help="Pexels API key. If not provided, use PEXELS_API_KEY env var.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing product images.",
        )

    def handle(self, *args, **kwargs):
        API_KEY = kwargs.get("api_key") or os.getenv("PEXELS_API_KEY", "")
        if not API_KEY:
            print("ERROR: PEXELS_API_KEY is not set. You can also pass --api-key.")
            return

        headers = {
            "Authorization": API_KEY
        }

        for product in Product.objects.all():
            if product.image and not kwargs.get("force"):
                print(f"SKIP (already has image): {product.name}")
                continue

            matched_query = None

            # 1. 找花種
            for keyword, query in FLOWER_KEYWORDS:
                if keyword in product.name:
                    matched_query = query
                    break

            # 沒有符合花種 → 不處理
            if not matched_query:
                print(f"SKIP (no flower match): {product.name}")
                continue

            print(f"Searching: {product.name} → {matched_query}")

            url = "https://api.pexels.com/v1/search"
            params = {
                "query": f"{matched_query} {product.name}",
                "per_page": 15
            }

            try:
                response = requests.get(url, headers=headers, params=params, timeout=10)

                if response.status_code != 200:
                    print("PEXELS FAIL:", response.status_code, response.text)
                    continue

                data = response.json()
                photos = data.get("photos")

                if not photos:
                    print("NO IMAGE FOUND")
                    continue

                photo = random.choice(photos)
                img_url = photo["src"]["medium"]

                img_response = requests.get(img_url, timeout=10)

                if img_response.status_code == 200:

                    filename = product.name.replace(" ", "_")

                    product.image.save(
                        f"{filename}.jpg",
                        ContentFile(img_response.content),
                        save=True
                    )

                    print("OK")

                else:
                    print("IMAGE DOWNLOAD FAIL")

            except Exception as e:
                print("ERROR:", e)
from django.core.management.base import BaseCommand

from catalog.models import Product
from catalog.management.commands.flower_keywords import FLOWER_KEYWORDS


def _has_flower_keyword(name):
    if not name:
        return False
    for keyword, _ in FLOWER_KEYWORDS:
        if keyword in name:
            return True
    return False


class Command(BaseCommand):
    help = "Remove products whose name does not contain a flower keyword from FLOWER_KEYWORDS."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only list products that would be removed without deleting them.",
        )
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Actually delete matching products. Without this option, the command will only preview.",
        )

    def handle(self, *args, **options):
        products = Product.objects.all()
        to_remove = [product for product in products if not _has_flower_keyword(product.name)]

        if not to_remove:
            self.stdout.write(self.style.SUCCESS("No products found without flower keyword in their name."))
            return

        self.stdout.write(self.style.WARNING(f"Found {len(to_remove)} product(s) without flower keyword:"))
        for product in to_remove:
            self.stdout.write(f"- {product.pk}: {product.name}")

        if not options["confirm"]:
            self.stdout.write(self.style.NOTICE("Use --confirm to delete these products."))
            return

        deleted_count = 0
        for product in to_remove:
            product.delete()
            deleted_count += 1

        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted_count} product(s)."))

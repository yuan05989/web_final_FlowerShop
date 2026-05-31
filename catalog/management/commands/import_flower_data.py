from decimal import Decimal
from pathlib import Path

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand

from catalog.models import Category, Product


class Command(BaseCommand):
    help = "Import products from flower_data.xlsx into the catalog app."

    def add_arguments(self, parser):
        parser.add_argument(
            "--excel",
            default=None,
            help="Path to the Excel file. Defaults to BASE_DIR.parent / flower_data.xlsx.",
        )
        parser.add_argument(
            "--sheet",
            default=0,
            help="Sheet name or index to read from the Excel file.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be imported without saving changes.",
        )

    def handle(self, *args, **options):
        excel_path = Path(options["excel"]) if options["excel"] else Path(settings.BASE_DIR).parent / "flower_data.xlsx"
        if not excel_path.exists():
            self.stderr.write(f"Excel file not found: {excel_path}")
            raise SystemExit(1)

        df = pd.read_excel(excel_path, sheet_name=options["sheet"])
        normalized_columns = {str(column).strip().lower(): column for column in df.columns if str(column).strip()}

        def get_value(row, key):
            column_name = normalized_columns.get(key)
            if column_name is None:
                return None
            value = row[column_name]
            if pd.isna(value):
                return None
            return value

        name_key = "name"
        price_key = "price"
        stock_key = "stock"
        category_key = "category"
        flower_category_key = "flower_category"

        total = 0
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for index, row in df.iterrows():
            name = get_value(row, name_key)
            if not name:
                skipped_count += 1
                continue
            name = str(name).strip()

            category_name = get_value(row, category_key)
            flower_category = get_value(row, flower_category_key)
            if not category_name and flower_category:
                category_name = flower_category

            if not category_name:
                self.stderr.write(f"Skipping product without category: {name}")
                skipped_count += 1
                continue

            category_name = str(category_name).strip()
            price_value = get_value(row, price_key)
            if price_value is None:
                self.stderr.write(f"Skipping product without price: {name}")
                skipped_count += 1
                continue
            price = Decimal(str(price_value)).quantize(Decimal("0.01"))

            stock_value = get_value(row, stock_key)
            stock = int(stock_value) if stock_value is not None else 0

            description_parts = []
            if flower_category and str(flower_category).strip() and str(flower_category).strip() != str(category_name).strip():
                description_parts.append(f"次分類：{flower_category}")
            description = "；".join(description_parts)

            category, _ = Category.objects.get_or_create(name=category_name)
            defaults = {
                "category": category,
                "price": price,
                "stock": stock,
                "description": description,
            }

            product, created = Product.objects.get_or_create(name=name, defaults=defaults)
            if created:
                created_count += 1
            else:
                changed = False
                for field_name, value in defaults.items():
                    if getattr(product, field_name) != value:
                        setattr(product, field_name, value)
                        changed = True
                if changed:
                    if not options["dry_run"]:
                        product.save()
                    updated_count += 1

            total += 1
            if options["dry_run"]:
                self.stdout.write(f"DRY RUN: {name} -> {category_name}, price={price}, stock={stock}")

        if not options["dry_run"]:
            self.stdout.write(self.style.SUCCESS(f"Imported {total} rows: {created_count} created, {updated_count} updated, {skipped_count} skipped."))
        else:
            self.stdout.write(self.style.WARNING(f"Dry run complete: {total} rows processed, {created_count} would be created, {updated_count} would be updated, {skipped_count} skipped."))

from decimal import Decimal
from pathlib import Path

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand

from catalog.models import Category, FlowerKind, Product


class Command(BaseCommand):
    help = "Import products from flower_products.xlsx into the catalog app."

    def add_arguments(self, parser):
        parser.add_argument(
            "--excel",
            default=None,
            help="Path to the Excel file. Defaults to BASE_DIR.parent / data / flower_products.xlsx.",
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
        default_excel_path = Path(settings.BASE_DIR).parent / "data" / "flower_products.xlsx"
        excel_path = Path(options["excel"]) if options["excel"] else default_excel_path
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

        def split_flower_types(raw_value):
            if raw_value is None:
                return []

            normalized = str(raw_value).strip()
            if not normalized:
                return []

            for separator in ("、", ",", ";", "/", "|"):
                normalized = normalized.replace(separator, ",")
            return [part.strip() for part in normalized.split(",") if part.strip()]

        required_keys = ("name", "category", "type", "festival", "price", "stock")
        missing_keys = [key for key in required_keys if key not in normalized_columns]
        if missing_keys:
            self.stderr.write(f"Missing required columns: {', '.join(missing_keys)}")
            raise SystemExit(1)

        total = 0
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for _, row in df.iterrows():
            name = get_value(row, "name")
            if not name:
                skipped_count += 1
                continue
            name = str(name).strip()

            category_name = get_value(row, "category")
            if not category_name:
                self.stderr.write(f"Skipping product without category: {name}")
                skipped_count += 1
                continue
            category_name = str(category_name).strip()

            price_value = get_value(row, "price")
            if price_value is None:
                self.stderr.write(f"Skipping product without price: {name}")
                skipped_count += 1
                continue
            price = Decimal(str(price_value)).quantize(Decimal("0.01"))

            stock_value = get_value(row, "stock")
            stock = int(stock_value) if stock_value is not None else 0

            festival_value = get_value(row, "festival")
            festival = str(festival_value).strip() if festival_value is not None else ""

            type_names = split_flower_types(get_value(row, "type"))

            product = Product.objects.prefetch_related("type").filter(name=name).first()
            is_created = product is None
            type_changed = False

            if is_created:
                created_count += 1
            else:
                existing_type_names = set(product.type.values_list("name", flat=True))
                incoming_type_names = set(type_names)
                type_changed = existing_type_names != incoming_type_names

                changed = (
                    product.category.name != category_name
                    or product.festival != festival
                    or product.price != price
                    or product.stock != stock
                    or type_changed
                )
                if changed:
                    updated_count += 1

            total += 1
            if options["dry_run"]:
                self.stdout.write(
                    f"DRY RUN: {name} -> category={category_name}, festival={festival}, price={price}, stock={stock}, type={type_names}"
                )
                continue

            category, _ = Category.objects.get_or_create(name=category_name)
            if is_created:
                product = Product.objects.create(
                    name=name,
                    category=category,
                    festival=festival,
                    price=price,
                    stock=stock,
                )
            else:
                product.category = category
                product.festival = festival
                product.price = price
                product.stock = stock
                product.save()

            product.type.set([FlowerKind.objects.get_or_create(name=type_name)[0] for type_name in type_names])

        if not options["dry_run"]:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Imported {total} rows: {created_count} created, {updated_count} updated, {skipped_count} skipped."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Dry run complete: {total} rows processed, {created_count} would be created, {updated_count} would be updated, {skipped_count} skipped."
                )
            )

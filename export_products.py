import csv

from catalog.models import Product


with open("products_export.csv", "w", newline="", encoding="utf-8-sig") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["id", "name", "festival", "type", "category", "price", "stock", "is_active"])

    for product in Product.objects.prefetch_related("type").select_related("category").all():
        writer.writerow(
            [
                product.id,
                product.name,
                product.festival,
                ", ".join(product.type.values_list("name", flat=True)),
                product.category.name,
                str(product.price),
                product.stock,
                product.is_active,
            ]
        )

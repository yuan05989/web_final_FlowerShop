import os
import django
from openpyxl import Workbook

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FlowerShop.settings")
django.setup()

from catalog.models import Product

wb = Workbook()
ws = wb.active
ws.title = "Products"

# 標題列
ws.append([
    "name",
    "category",
    "price",
    "stock",
    "type",
    "image"
])

products = Product.objects.all()

for p in products:
    ws.append([
        p.name,
        str(p.category),
        float(p.price),
        p.stock,
        str(p.type),
        str(p.image)
    ])

wb.save("products.xlsx")

print("Excel 已匯出：products.xlsx")
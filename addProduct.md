### 新增商品
```bash
#進入shell
python manage.py shell

#匯入Model
from catalog.models import Category, Product

#新增分類
flower = Category.objects.create(
    name="花束"
)

#新增多個商品
products = [
    {
        "name": "紅玫瑰花束",
        "price": 999,
        "stock": 10,
    },
    {
        "name": "畢業花束",
        "price": 1280,
        "stock": 5,
    },
    {
        "name": "母親節康乃馨",
        "price": 1580,
        "stock": 8,
    }
]

for item in products:
    Product.objects.create(
        category=flower,
        name=item["name"],
        price=item["price"],
        stock=item["stock"]
    )
```
from django.conf import settings
from django.db import models

from catalog.models import Product
from common.models import TimeStampedModel


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    SHIPPED = "shipped", "Shipped"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class Order(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order<{self.id}>"


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"OrderItem<{self.id}>"


class Cart(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")

    def __str__(self):
        return f"Cart<{self.user.username}>"

    @property
    def total_amount(self):
        return sum(item.line_total for item in self.items.select_related("product").all())


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["cart", "product"], name="unique_cart_product"),
        ]

    def __str__(self):
        return f"CartItem<{self.id}>"

    @property
    def unit_price(self):
        return self.product.price

    @property
    def line_total(self):
        return self.product.price * self.quantity

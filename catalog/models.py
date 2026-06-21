from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from common.models import TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class FlowerKind(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    festival = models.CharField(max_length=100, blank=True, help_text="Festival")
    type = models.ManyToManyField(FlowerKind, blank=True, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(price__gte=0), name="product_price_non_negative"),
        ]

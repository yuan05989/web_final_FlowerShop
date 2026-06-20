from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from catalog.models import Category, FlowerKind, Product


class ProductAPITest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Roses")
        self.rose_kind = FlowerKind.objects.create(name="Rose")
        self.peony_kind = FlowerKind.objects.create(name="Peony")
        self.product = Product.objects.create(
            category=self.category,
            name="Red Rose",
            festival="Valentine",
            price="199.00",
            stock=10,
            is_active=True,
        )
        self.product.type.set([self.rose_kind])
        self.user = User.objects.create_user(username="user", password="password123")
        self.admin = User.objects.create_user(username="admin", password="password123", is_staff=True)

    def test_product_list_public(self):
        response = self.client.get("/api/v1/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["festival"], "Valentine")
        self.assertEqual(response.data[0]["type_names"], ["Rose"])

    def test_product_create_requires_admin(self):
        self.client.login(username="user", password="password123")
        payload = {
            "category": self.category.id,
            "name": "White Rose",
            "festival": "Mother's Day",
            "type": [self.rose_kind.id],
            "price": "299.00",
            "stock": 8,
            "is_active": True,
        }
        response = self.client.post("/api/v1/products/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_create_by_admin(self):
        self.client.login(username="admin", password="password123")
        payload = {
            "category": self.category.id,
            "name": "Pink Rose",
            "festival": "Graduation",
            "type": [self.rose_kind.id, self.peony_kind.id],
            "price": "399.00",
            "stock": 5,
            "is_active": True,
        }
        response = self.client.post("/api/v1/products/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["festival"], "Graduation")
        self.assertEqual(response.data["type_names"], ["Rose", "Peony"])

    def test_product_update_type_by_admin(self):
        self.client.login(username="admin", password="password123")
        payload = {
            "category": self.category.id,
            "name": self.product.name,
            "festival": "Mother's Day",
            "type": [self.rose_kind.id, self.peony_kind.id],
            "description": self.product.description,
            "price": "199.00",
            "stock": 10,
            "is_active": True,
        }
        response = self.client.put(reverse("product-detail", args=[self.product.id]), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.festival, "Mother's Day")
        self.assertEqual(set(self.product.type.values_list("name", flat=True)), {"Rose", "Peony"})

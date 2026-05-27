from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from catalog.models import Category, Product


class ProductAPITest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Roses")
        self.product = Product.objects.create(
            category=self.category,
            name="Red Rose",
            price="199.00",
            stock=10,
            is_active=True,
        )
        self.user = User.objects.create_user(username="user", password="password123")
        self.admin = User.objects.create_user(username="admin", password="password123", is_staff=True)

    def test_product_list_public(self):
        response = self.client.get("/api/v1/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_product_create_requires_admin(self):
        self.client.login(username="user", password="password123")
        payload = {
            "category": self.category.id,
            "name": "White Rose",
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
            "price": "399.00",
            "stock": 5,
            "is_active": True,
        }
        response = self.client.post("/api/v1/products/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

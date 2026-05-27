from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from catalog.models import Category, Product
from orders.models import Order


class OrderAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="password123")
        self.other = User.objects.create_user(username="other", password="password123")
        category = Category.objects.create(name="Tulips")
        self.product = Product.objects.create(
            category=category,
            name="Yellow Tulip",
            price="100.00",
            stock=20,
            is_active=True,
        )

    def test_order_create_and_total(self):
        self.client.login(username="buyer", password="password123")
        payload = {"items": [{"product_id": self.product.id, "quantity": 3}]}
        response = self.client.post("/api/v1/orders/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["total_amount"], "300.00")

    def test_order_access_owner_only(self):
        order = Order.objects.create(user=self.user, total_amount="100.00")
        self.client.login(username="other", password="password123")
        response = self.client.get(f"/api/v1/orders/{order.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile
from catalog.models import Category, Product
from orders.models import Order


class WebFlowTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Roses", description="Rose flowers")
        self.active_product = Product.objects.create(
            category=self.category,
            name="Red Rose Bouquet",
            description="Fresh bouquet",
            price="300.00",
            stock=10,
            is_active=True,
        )
        self.inactive_product = Product.objects.create(
            category=self.category,
            name="Old Rose",
            description="Hidden",
            price="100.00",
            stock=5,
            is_active=False,
        )
        self.user = User.objects.create_user(username="buyer", password="password123")

    def test_register_success(self):
        response = self.client.post(
            reverse("web:register"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "first_name": "New",
                "last_name": "User",
                "password1": "password123",
                "password2": "password123",
                "phone": "0911222333",
                "address": "Taipei",
            },
        )
        self.assertRedirects(response, reverse("web:product-list"))
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertTrue(UserProfile.objects.filter(user__username="newuser").exists())

    def test_product_list_only_active(self):
        response = self.client.get(reverse("web:product-list"))
        self.assertContains(response, "Red Rose Bouquet")
        self.assertNotContains(response, "Old Rose")

    def test_product_search(self):
        response = self.client.get(reverse("web:product-list"), {"q": "Red"})
        self.assertContains(response, "Red Rose Bouquet")

    def test_order_requires_login(self):
        response = self.client.post(reverse("web:order-create", kwargs={"pk": self.active_product.pk}), {"quantity": 1})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("web:login"), response.url)

    def test_order_create_success_and_stock_reduce(self):
        self.client.login(username="buyer", password="password123")
        response = self.client.post(reverse("web:order-create", kwargs={"pk": self.active_product.pk}), {"quantity": 2})
        order = Order.objects.first()
        self.assertRedirects(response, reverse("web:order-detail", kwargs={"pk": order.pk}))
        self.active_product.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(str(order.total_amount), "600.00")
        self.assertEqual(self.active_product.stock, 8)

    def test_order_create_insufficient_stock(self):
        self.client.login(username="buyer", password="password123")
        response = self.client.post(reverse("web:order-create", kwargs={"pk": self.active_product.pk}), {"quantity": 999})
        self.assertRedirects(response, reverse("web:product-detail", kwargs={"pk": self.active_product.pk}))
        self.assertEqual(Order.objects.count(), 0)

    def test_order_detail_owner_only(self):
        owner_order = Order.objects.create(user=self.user, total_amount="100.00")
        other = User.objects.create_user(username="other", password="password123")
        self.client.login(username="other", password="password123")
        response = self.client.get(reverse("web:order-detail", kwargs={"pk": owner_order.pk}))
        self.assertEqual(response.status_code, 404)

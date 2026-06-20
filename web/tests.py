from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile
from catalog.models import Category, FlowerKind, Product
from orders.models import Order


class WebFlowTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Roses", description="Rose flowers")
        self.other_category = Category.objects.create(name="Tulips", description="Tulip flowers")
        self.rose_kind = FlowerKind.objects.create(name="Rose")
        self.peony_kind = FlowerKind.objects.create(name="Peony")
        self.active_product = Product.objects.create(
            category=self.category,
            name="Red Rose Bouquet",
            description="Fresh bouquet",
            festival="Valentine",
            price="300.00",
            stock=10,
            is_active=True,
        )
        self.active_product.type.set([self.rose_kind, self.peony_kind])
        self.other_product = Product.objects.create(
            category=self.other_category,
            name="Spring Tulip Bundle",
            description="Bright flowers",
            festival="Graduation",
            price="400.00",
            stock=6,
            is_active=True,
        )
        self.other_product.type.set([self.peony_kind])
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
        self.assertContains(response, "花種：Rose, Peony")
        self.assertContains(response, "節日：Valentine")
        self.assertNotContains(response, "Old Rose")

    def test_product_search(self):
        response = self.client.get(reverse("web:product-list"), {"q": "Red"})
        product_names = [product.name for product in response.context["products"]]
        self.assertEqual(product_names, ["Red Rose Bouquet"])

    def test_product_type_search(self):
        response = self.client.get(reverse("web:product-list"), {"type": str(self.rose_kind.id)})
        product_names = [product.name for product in response.context["products"]]
        self.assertEqual(product_names, ["Red Rose Bouquet"])

    def test_product_detail_shows_name_then_type_then_festival_then_description(self):
        response = self.client.get(reverse("web:product-detail", kwargs={"pk": self.active_product.pk}))
        content = response.content.decode("utf-8")
        self.assertTrue(content.index("Red Rose Bouquet") < content.index("花種：Rose, Peony"))
        self.assertTrue(content.index("花種：Rose, Peony") < content.index("節日：Valentine"))
        self.assertTrue(content.index("節日：Valentine") < content.index("Fresh bouquet"))

    def test_staff_login_link_visible(self):
        response = self.client.get(reverse("web:product-list"))
        self.assertContains(response, "工作人員登入")
        self.assertContains(response, "/admin/")

    def test_featured_carousel_visible(self):
        response = self.client.get(reverse("web:product-list"))
        self.assertContains(response, "featuredCarousel")
        self.assertContains(response, "carousel-item active")

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

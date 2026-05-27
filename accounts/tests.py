from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AccountsAPITest(APITestCase):
    def test_register_success(self):
        payload = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
            "phone": "0911222333",
        }
        response = self.client.post(reverse("register"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(username="alice").count(), 1)

    def test_login_failure(self):
        User.objects.create_user(username="bob", password="password123")
        payload = {"username": "bob", "password": "wrong-password"}
        response = self.client.post(reverse("login"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

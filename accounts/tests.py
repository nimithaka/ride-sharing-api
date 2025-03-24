from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_rider_registration(self):
        data = {
            "username": "testrider",
            "password": "testpass123",
            "email": "rider@test.com",
            "first_name": "Test",
            "last_name": "Rider",
            "user_type": "rider",
            "phone_number": "1234567890",
            "latitude": 0,
            "longitude": 0,
        }
        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().user_type, "rider")

    def test_driver_registration(self):
        data = {
            "username": "testdriver",
            "password": "testpass123",
            "email": "driver@test.com",
            "first_name": "Test",
            "last_name": "Driver",
            "user_type": "driver",
            "phone_number": "1234567890",
            "latitude": 0,
            "longitude": 0,
            "is_available": True,
        }
        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().user_type, "driver")
        self.assertTrue(User.objects.get().is_available)

    def test_login(self):
        # Create a user first
        User.objects.create_user(
            username="testuser", password="testpass123", user_type="rider"
        )

        # Try to login
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(reverse("login"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user_type"], "rider")

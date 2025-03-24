from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.gis.geos import Point
from .models import Ride

User = get_user_model()


class RideModelTest(TestCase):
    def setUp(self):
        self.rider = User.objects.create_user(
            username="testrider", password="testpass", user_type="rider"
        )
        self.driver = User.objects.create_user(
            username="testdriver",
            password="testpass",
            user_type="driver",
            is_available=True,
        )

        # Create a test ride
        self.ride = Ride.objects.create(
            rider=self.rider,
            pickup_location=Point(0, 0),
            dropoff_location=Point(1, 1),
            status="requested",
        )

    def test_ride_creation(self):
        self.assertEqual(self.ride.status, "requested")
        self.assertEqual(self.ride.rider, self.rider)
        self.assertIsNone(self.ride.driver)


class RideAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.rider = User.objects.create_user(
            username="testrider", password="testpass", user_type="rider"
        )
        self.driver = User.objects.create_user(
            username="testdriver",
            password="testpass",
            user_type="driver",
            is_available=True,
        )

        # Login as rider
        response = self.client.post(
            reverse("login"), {"username": "testrider", "password": "testpass"}
        )
        self.rider_token = response.data["access"]

        # Login as driver
        response = self.client.post(
            reverse("login"), {"username": "testdriver", "password": "testpass"}
        )
        self.driver_token = response.data["access"]

    def test_create_ride(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.rider_token}")
        data = {
            "pickup_latitude": 0,
            "pickup_longitude": 0,
            "dropoff_latitude": 1,
            "dropoff_longitude": 1,
        }
        response = self.client.post(reverse("ride-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ride.objects.count(), 1)

    def test_driver_accept_ride(self):
        # Create a ride first
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.rider_token}")
        data = {
            "pickup_latitude": 0,
            "pickup_longitude": 0,
            "dropoff_latitude": 1,
            "dropoff_longitude": 1,
        }
        response = self.client.post(reverse("ride-list"), data)
        ride_id = response.data["id"]

        # Now have driver accept the ride
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.driver_token}")
        response = self.client.post(reverse("ride-accept-ride", args=[ride_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify ride status
        ride = Ride.objects.get(id=ride_id)
        self.assertEqual(ride.status, "matched")
        self.assertEqual(ride.driver, self.driver)

    def test_ride_status_update(self):
        # Create and accept a ride
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.rider_token}")
        data = {
            "pickup_latitude": 0,
            "pickup_longitude": 0,
            "dropoff_latitude": 1,
            "dropoff_longitude": 1,
        }
        response = self.client.post(reverse("ride-list"), data)
        ride_id = response.data["id"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.driver_token}")
        self.client.post(reverse("ride-accept-ride", args=[ride_id]))

        # Update status to in_progress
        response = self.client.post(
            reverse("ride-update-status", args=[ride_id]), {"status": "in_progress"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify ride status
        ride = Ride.objects.get(id=ride_id)
        self.assertEqual(ride.status, "in_progress")

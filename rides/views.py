from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.contrib.auth import get_user_model
from .models import Ride, RideLocationUpdate
from .serializers import (
    RideSerializer,
    RideStatusUpdateSerializer,
    RideLocationUpdateSerializer,
)
from accounts.serializers import UserSerializer

User = get_user_model()


class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer

    def get_queryset(self):
        user = self.request.user
        print(user.user_type)
        if user.user_type == "rider":
            print(Ride.objects.filter(rider=user))
            return Ride.objects.filter(rider=user)
        elif user.user_type == "driver":
            return Ride.objects.filter(driver=user) | Ride.objects.filter(
                status="requested", driver__isnull=True
            )
        return Ride.objects.none()

    def perform_create(self, serializer):
        serializer.save(rider=self.request.user)

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        ride = self.get_object()
        user = request.user
        user_role = "rider" if request.user.user_type == "rider" else "driver"
        serializer = RideStatusUpdateSerializer(data=request.data)

        if serializer.is_valid():
            new_status = serializer.validated_data["status"]
            allowed_transitions = {
                "rider": {
                    "requested": ["cancelled"],
                    "cancelled": [],
                },
                "driver": {
                    "requested": ["matched", "cancelled"],
                    "matched": ["in_progress", "cancelled"],
                    "in_progress": ["completed", "cancelled"],
                    "completed": [],
                    "cancelled": [],
                },
            }

            if user_role == "rider" and new_status in [
                "in_progress",
                "completed",
                "matched",
            ]:
                return Response(
                    {
                        "error": "Riders are not allowed to set the ride status to in_progress or completed"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            if new_status not in allowed_transitions[user_role].get(ride.status, []):
                return Response(
                    {"error": f"Cannot transition from {ride.status} to {new_status}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            ride.status = new_status
            ride.save()

            # Mark driver as available, after a ride completed or cancelled
            if user_role == "driver" and new_status in ["completed", "cancelled"]:
                user.is_available = True
                user.save()

            return Response(RideSerializer(ride).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def accept_ride(self, request, pk=None):
        ride = self.get_object()
        user = request.user

        if user.user_type != "driver":
            return Response(
                {"error": "Only drivers can accept rides"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if ride.status != "requested":
            return Response(
                {"error": "This ride is not available for acceptance"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_available:
            return Response(
                {"error": "You are not marked as available"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ride.driver = user
        ride.status = "matched"
        ride.save()

        # Mark driver as unavailable
        user.is_available = False
        user.save()

        return Response(RideSerializer(ride).data)

    @action(detail=True, methods=["post"])
    def update_location(self, request, pk=None):
        ride = self.get_object()
        user = request.user
        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")

        # Ensure only the driver can update location
        if ride.driver != request.user:
            return Response(
                {"error": "Only the assigned driver can update the ride location"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Ensure the ride is in progress
        if ride.status != "in_progress":
            return Response(
                {"error": "Can only update location for in-progress rides"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RideLocationUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ride=ride)
            if latitude and longitude:
                user.current_location = Point(
                    float(longitude), float(latitude)
                )  # (lng, lat) format
                user.save()
            return Response(RideSerializer(ride).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NearbyDriversView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        ride_id = self.kwargs.get("ride_id")
        user = self.request.user
        try:
            ride = Ride.objects.get(id=ride_id)
            if user not in [ride.rider, ride.driver] or ride.status in [
                "matched",
                "in-progress",
                "completed",
                "cancelled",
            ]:
                raise PermissionDenied("You cannot view nearby drivers for this ride.")
            # Get available drivers within 5km of the pickup location
            return (
                User.objects.filter(
                    user_type="driver",
                    is_available=True,
                    current_location__isnull=False,
                    current_location__distance_lte=(ride.pickup_location, D(km=1)),
                )
                .annotate(distance=Distance("current_location", ride.pickup_location))
                .order_by("distance")
            )
        except Ride.DoesNotExist:
            return User.objects.none()

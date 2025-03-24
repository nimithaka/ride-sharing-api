from rest_framework import serializers
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.contrib.auth import get_user_model
from .models import Ride, RideLocationUpdate

User = get_user_model()


class RideSerializer(serializers.ModelSerializer):
    pickup_latitude = serializers.FloatField(write_only=True)
    pickup_longitude = serializers.FloatField(write_only=True)
    dropoff_latitude = serializers.FloatField(write_only=True)
    dropoff_longitude = serializers.FloatField(write_only=True)
    rider_name = serializers.SerializerMethodField()
    driver_name = serializers.SerializerMethodField()

    class Meta:
        model = Ride
        fields = [
            "id",
            "rider",
            "driver",
            "rider_name",
            "driver_name",
            "pickup_latitude",
            "pickup_longitude",
            "dropoff_latitude",
            "dropoff_longitude",
            "current_location",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "rider",
            "driver",
            "current_location",
            "status",
            "created_at",
            "updated_at",
        ]

    def get_rider_name(self, obj):
        return obj.rider.get_full_name() or obj.rider.username

    def get_driver_name(self, obj):
        if obj.driver:
            return obj.driver.get_full_name() or obj.driver.username
        return None

    def create(self, validated_data):
        pickup_lat = validated_data.pop("pickup_latitude")
        pickup_lng = validated_data.pop("pickup_longitude")
        dropoff_lat = validated_data.pop("dropoff_latitude")
        dropoff_lat = validated_data.pop("dropoff_longitude")
        validated_data["pickup_location"] = Point(float(pickup_lng), float(pickup_lat))
        validated_data["dropoff_location"] = Point(
            float(dropoff_lat), float(dropoff_lat)
        )
        validated_data["current_location"] = validated_data["pickup_location"]

        return super().create(validated_data)


class RideStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Ride.STATUS_CHOICES)


class RideLocationUpdateSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)

    class Meta:
        model = RideLocationUpdate
        fields = ["id", "ride", "location", "timestamp", "latitude", "longitude"]
        read_only_fields = ["id", "ride", "location", "timestamp"]

    def create(self, validated_data):
        latitude = validated_data.pop("latitude")
        longitude = validated_data.pop("longitude")

        validated_data["location"] = Point(float(longitude), float(latitude))

        # Update the ride's current location as well
        ride = validated_data["ride"]
        ride.current_location = validated_data["location"]
        ride.save()

        return super().create(validated_data)

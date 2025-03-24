from django.db import models
from django.contrib.gis.db import models as gis_models
from django.conf import settings


class Ride(models.Model):
    STATUS_CHOICES = (
        ("requested", "Requested"),
        ("matched", "Matched"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="rides_as_rider",
        on_delete=models.CASCADE,
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="rides_as_driver",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    pickup_location = gis_models.PointField(geography=True)
    dropoff_location = gis_models.PointField(geography=True)
    current_location = gis_models.PointField(geography=True, blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="requested"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ride {self.id} - {self.get_status_display()}"


class RideLocationUpdate(models.Model):
    """Model for tracking a ride's location over time"""

    ride = models.ForeignKey(
        Ride, related_name="location_updates", on_delete=models.CASCADE
    )
    location = gis_models.PointField(geography=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Location update for Ride {self.ride.id} at {self.timestamp}"

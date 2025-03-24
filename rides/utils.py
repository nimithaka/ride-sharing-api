from django.contrib.gis.measure import Distance as GeographicDistance
from django.contrib.gis.db.models.functions import Distance
from django.contrib.auth import get_user_model
from .models import Ride

User = get_user_model()


def find_nearest_drivers(ride, max_distance_km=5, limit=5):
    """
    Find the nearest available drivers to a ride pickup location

    Args:
        ride: Ride object
        max_distance_km: Maximum distance in kilometers to search
        limit: Maximum number of drivers to return

    Returns:
        QuerySet of User objects (drivers) ordered by distance
    """
    return (
        User.objects.filter(
            user_type="driver",
            is_available=True,
            current_location__distance_lte=(
                ride.pickup_location,
                GeographicDistance(km=max_distance_km),
            ),
        )
        .annotate(distance=Distance("current_location", ride.pickup_location))
        .order_by("distance")[:limit]
    )


def auto_match_ride(ride):
    """
    Automatically match a ride with the nearest available driver

    Args:
        ride: Ride object

    Returns:
        (bool, str): (success, message)
    """
    if ride.status != "requested":
        return False, "Ride is not in 'requested' status"

    if ride.driver:
        return False, "Ride already has a driver assigned"

    nearest_drivers = find_nearest_drivers(ride, max_distance_km=5, limit=1)

    if not nearest_drivers.exists():
        return False, "No available drivers nearby"

    driver = nearest_drivers.first()
    ride.driver = driver
    ride.status = "matched"
    ride.save()

    # Mark driver as unavailable
    driver.is_available = False
    driver.save()

    return True, f"Ride matched with driver {driver.username}"

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.gis.db import models as gis_models


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ("rider", "Rider"),
        ("driver", "Driver"),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    current_location = gis_models.PointField(geography=True, blank=True, null=True)
    is_available = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

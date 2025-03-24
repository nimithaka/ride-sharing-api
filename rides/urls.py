from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RideViewSet, NearbyDriversView

router = DefaultRouter()
router.register(r"", RideViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "nearby-drivers/<int:ride_id>/",
        NearbyDriversView.as_view(),
        name="nearby-drivers",
    ),
]

from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.gis.geos import Point

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    latitude = serializers.FloatField(write_only=True, required=False)
    longitude = serializers.FloatField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "user_type",
            "phone_number",
            "latitude",
            "longitude",
            "is_available",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        latitude = validated_data.pop("latitude", None)
        longitude = validated_data.pop("longitude", None)

        password = validated_data.pop("password", None)
        user = User.objects.create(**validated_data)

        if password:
            user.set_password(password)

        if latitude and longitude:
            user.current_location = Point(longitude, latitude)

        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data.update(
            {
                "user_id": user.id,
                "username": user.username,
                "user_type": user.user_type,
            }
        )
        return data

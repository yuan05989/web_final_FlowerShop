from django.contrib.auth.models import User
from rest_framework import serializers

from accounts.models import UserProfile


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    address = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name", "phone", "address"]

    def create(self, validated_data):
        phone = validated_data.pop("phone", "")
        address = validated_data.pop("address", "")
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        UserProfile.objects.create(user=user, phone=phone, address=address)
        return user


class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source="profile.phone", read_only=True)
    address = serializers.CharField(source="profile.address", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "phone", "address"]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

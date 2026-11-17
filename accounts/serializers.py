
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from rest_framework import serializers

from .models import Profile


class RegistrationSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    phone = serializers.CharField(
        max_length=15,
        min_length=10,
        required=True
    )

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

    confirm_password = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "password",
            "confirm_password",
        ]

    def validate_email(self, value):
        email = value.strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "This email is already registered."
            )

        return email

    def validate_phone(self, value):
        phone = value.strip()

        if User.objects.filter(username=phone).exists():
            raise serializers.ValidationError(
                "This phone number is already registered."
            )

        return phone

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        return data

    @transaction.atomic
    def create(self, validated_data):

        validated_data.pop("confirm_password")

        password = validated_data.pop("password")
        phone = validated_data.pop("phone")

        user = User(
            username=phone,
            **validated_data
        )

        user.set_password(password)
        user.save()

        Profile.objects.create(
            user=user,
            phone=phone
        )

        return user

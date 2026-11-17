
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Profile


class RegistrationForm(forms.ModelForm):

    phone = forms.CharField(
        max_length=15,
        min_length=10,
        required=True,
        label="Phone Number"
    )

    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Password"
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()

        if User.objects.filter(username=phone).exists():
            raise forms.ValidationError(
                "This phone number is already registered."
            )

        return phone

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "This email is already registered."
            )

        return email

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:

            if password != confirm_password:
                self.add_error(
                    "confirm_password",
                    "Passwords do not match."
                )

            else:
                try:
                    validate_password(password)
                except ValidationError as error:
                    self.add_error("password", error)

        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):

        user = super().save(commit=False)

        user.username = self.cleaned_data["phone"]

        user.set_password(
            self.cleaned_data["password"]
        )

        if commit:
            user.save()

            Profile.objects.create(
                user=user,
                phone=self.cleaned_data["phone"]
            )

        return user

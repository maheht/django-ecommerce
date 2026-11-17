
from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):

    class Meta:
        model = Order

        fields = [
            "recipient_name",
            "phone",
            "city",
            "address",
            "postal_code",
        ]

        widgets = {
            "recipient_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Recipient name",
            }),

            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Phone number",
            }),

            "city": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "City",
            }),

            "address": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Full delivery address",
                "rows": 4,
            }),

            "postal_code": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Postal code",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make all delivery fields required
        for field in self.fields.values():
            field.required = True

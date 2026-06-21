from django import forms
from django.contrib.auth.models import User


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, min_length=8)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, min_length=8)
    phone = forms.CharField(max_length=20, required=False)
    address = forms.CharField(max_length=255, required=False)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data


class OrderCreateForm(forms.Form):
    quantity = forms.IntegerField(min_value=1)


class CartAddForm(forms.Form):
    quantity = forms.IntegerField(min_value=1)

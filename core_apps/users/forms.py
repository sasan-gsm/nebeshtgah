from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django import forms
from .models import User


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, help_text="Required. Enter a valid email address."
    )
    first_name = forms.CharField(max_length=60, required=False)
    last_name = forms.CharField(max_length=60, required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                _("This email is already in use. Please use a different email.")
            )
        return email


class CustomUserLoginForm(forms.Form):
    email_or_username = forms.CharField(label="Email or Username")
    # username_or_email = forms.CharField(
    #     label="Username or Email",
    #     max_length=150,
    #     widget=forms.TextInput(attrs={'autofocus': True}),
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter your password",
                "class": "password-field",
                "autocomplete": "current-password",
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        email_or_username = cleaned_data.get("username_or_email")
        password = cleaned_data.get("password")
        return cleaned_data


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"

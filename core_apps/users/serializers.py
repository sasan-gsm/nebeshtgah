from allauth.account.utils import url_str_to_user_pk
from allauth.account.forms import ResetPasswordForm, SetPasswordForm
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer, PasswordChangeSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from dj_rest_auth.serializers import (
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
)
from allauth.account.forms import ResetPasswordKeyForm
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from typing import Dict, Any
from django.contrib.auth import get_user_model
from .tasks import send_password_reset_email
from django.db import transaction
from profiles.models import Profile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "first_name", "last_name")
        extra_kwargs = {"password": {"write_only": True}}
        # fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser']

    def create(self, validated_data):
        # Create a new user with hashed password
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(source="profile.avatar", required=False)
    phone_number = serializers.CharField(source="profile.phone_number", required=False)
    gender = serializers.ChoiceField(
        source="profile.gender", choices=Profile.gender.choices, required=False
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "avatar",
            "phone_number",
            "gender",
        )
        read_only_fields = ("id", "email")


def update(self, instance: User, validated_data: Dict[str, Any]):  # type: ignore
    with transaction.atomic():
        list(
            map(
                lambda kv: setattr(instance, *kv),
                filter(
                    lambda kv: kv[0] in {f.name for f in User._meta.get_fields()},
                    validated_data.items(),
                ),
            )
        )
        list(
            map(
                lambda kv: setattr(instance.profile, *kv),
                filter(
                    lambda kv: kv[0] in {f.name for f in Profile._meta.get_fields()},
                    validated_data.items(),
                ),
            )
        )
        instance.profile.save(), instance.save()
        return instance


class CustomRegisterSerializer(RegisterSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "email",
            "password1",
            "password2",
            "first_name",
            "last_name",
        )

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def validate_username_email(self, data):
        username = data.get("username")
        email = data.get("email")

        # Check if a user with the same username or email already exists
        if User.objects.filter(Q(username=username) | Q(email=email)).exists():
            raise serializers.ValidationError(
                "Username and/or Email is already in use."
            )
        return data

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password1"])
        user.is_active = True
        user.save()
        setup_user_email(request, user, self)
        return user


class CustomLoginSerializer(LoginSerializer):
    login = serializers.CharField(
        required=True, help_text=_("User's login identifier.")
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
        help_text=_("User's password."),
    )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        login: str = attrs.get("username")
        password: str = attrs.get("password")

        if login and password:
            user = authenticate(
                request=self.context.get("request"), username=login, password=password
            )

            if not user:
                raise serializers.ValidationError(
                    _("Unable to log in with provided credentials."),
                    code="authorization",
                )
        else:
            raise serializers.ValidationError(
                _('Must include "email" and "password".'), code="authorization"
            )

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        }


class CustomPasswordResetSerializer(PasswordResetSerializer):
    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        # Validate that the email exists in the system
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("User with this email does not exist."))
        return value

    def save(self) -> None:
        """Use allauth's form to generate and send the reset email via Celery."""
        request = self.context.get("request")
        email = self.validated_data["email"]
        reset_form = ResetPasswordForm(data={"email": email})
        if reset_form.is_valid():
            reset_form.save(
                request=request,
                use_https=request.is_secure(),
                from_email=None,  # Uses settings.DEFAULT_FROM_EMAIL
            )
        send_password_reset_email.delay(email, reset_form.generate_reset_url(request))


class CustomPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):
    uid: serializers.CharField = serializers.CharField(required=True)
    token: serializers.CharField = serializers.CharField(required=True)
    new_password1: serializers.CharField = serializers.CharField(write_only=True)
    new_password2: serializers.CharField = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None  # Initialize user attribute

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the token, uid, and password match."""
        uid = attrs.get("uid")
        token = attrs.get("token")
        new_password1 = attrs.get("new_password1")
        new_password2 = attrs.get("new_password2")

        # Decode uid to get user
        try:
            user_id = url_str_to_user_pk(uid)
            user = User.objects.get(pk=user_id, is_active=True)
        except (ValueError, User.DoesNotExist, TypeError):
            raise serializers.ValidationError({"uid": "Invalid or inactive user."})

        # Validate the token using Allauth ResetPasswordKeyForm
        reset_form = ResetPasswordKeyForm(user=user, data={"key": token})
        if not reset_form.is_valid():
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        # Validate passwords
        if new_password1 != new_password2:
            raise serializers.ValidationError(
                {"new_password2": "Passwords do not match."}
            )
        self.user = user
        return attrs

    def save(self) -> None:
        """Set the new password and clear the token."""
        user = self.user
        new_password = self.validated_data["new_password1"]

        # Use allauth's SetPasswordForm for consistency
        form = SetPasswordForm(
            user=user,
            data={"new_password1": new_password, "new_password2": new_password},
        )
        if form.is_valid():
            form.save()
        else:
            raise serializers.ValidationError(form.errors)


class CustomPasswordChangeSerializer(PasswordChangeSerializer):
    old_password = serializers.CharField()
    new_password1 = serializers.CharField()
    new_password2 = serializers.CharField()

    def validate(self, attrs):
        if attrs["new_password1"] != attrs["new_password2"]:
            raise ValidationError(_("New passwords do not match."))

        if not self.context["request"].user.check_password(attrs["old_password"]):
            raise ValidationError(_("Old password is incorrect."))
        return attrs

from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from typing import Dict, Any
from django.contrib.auth import get_user_model


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}


class CustomRegisterSerializer(RegisterSerializer):
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

    def validate_email(self, email: str):
        return super().validate_email(email)

    def validate_username(self, username: str):
        return super().validate_username(username)

    def save(self, request):
        user = super().save(request)
        # Perform any additional actions here, if needed
        return user


class CustomLoginSerializer(LoginSerializer):
    login = serializers.CharField()

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        login: str = attrs.get("login")
        password: str = attrs.get("password")

        if "@" in login:  # Email login
            username = User.objects.filter(email=login).first()
        else:  # Username login
            username = User.objects.filter(username=login).first()

        if not username:
            raise serializers.ValidationError(_("Invalid login credentials"))

        authenticated_user = authenticate(username=username.username, password=password)

        if not authenticated_user:
            raise serializers.ValidationError(_("Invalid login credentials"))

        refresh = RefreshToken.for_user(authenticated_user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": authenticated_user.id,
                "username": authenticated_user.username,
                "email": authenticated_user.email,
            },
        }

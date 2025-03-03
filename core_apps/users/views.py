from typing import Any
from django.urls import reverse
from rest_framework import generics, status
from rest_framework.response import Response
from dj_rest_auth.views import (
    LogoutView,
    LoginView,
    PasswordResetView,
    PasswordResetConfirmView,
)
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from .serializers import PasswordResetSerializer, PasswordResetConfirmSerializer
from .signals import update_user_last_login
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _


class CustomLoginView(LoginView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = self.request.user
        update_user_last_login.send(
            sender=self.__class__, instance=user, request=request
        )
        return response


class CustomLogOutView(LogoutView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return Response({"detail": _("Logout Successful")}, status=status.HTTP_200_OK)


class CustomPasswordResetView(PasswordResetView):
    serializer_class = PasswordResetSerializer
    permission_classes = []  # Public endpoint
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    def get(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        """Render the browsable API form for password reset."""
        serializer = self.get_serializer()
        return Response(serializer.data)  # Empty form for GET

    def post(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        """Handle password reset request."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password reset email sent."},
            status=status.HTTP_200_OK,
            headers={"Location": request.build_absolute_uri(reverse("password-reset"))},
        )


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = []  # Public endpoint, token validates access
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    def get(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        """Render the browsable API form for password reset confirmation."""
        serializer = self.get_serializer()
        return Response(serializer.data)  # Empty form for GET

    def post(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        """Handle password reset confirmation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
            headers={"Location": request.build_absolute_uri(reverse("login"))},
        )

from typing import Any
from django.urls import reverse
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from .serializers import (
    UserSerializer,
    CustomLoginSerializer,
    CustomRegisterSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
)
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from .signals import update_user_last_login
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _


class UserViewSet(viewsets.GenericViewSet):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @action(methods=["POST"], detail=False)
    def register(self, request):
        serializer = CustomRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request)
        return Response(status=status.HTTP_201_CREATED)

    @action(methods="POST")
    def login(self, request):
        serializer = CustomLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Fire signal only if user is authenticated
        [
            update_user_last_login(
                sender="User", instance=request.user, request=request
            )
            for _ in [request.user]
            if getattr(request, "user", None) and request.user.is_authenticated
        ]
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @action(methods="POST")
    def logout(self, request):
        return Response(
            _("Successful, discard token."), status=status.HTTP_205_RESET_CONTENT
        )

    @action(methods=["POST"], detail=False)
    def password_reset(self, request):
        serializer = PasswordResetSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": _("Password reset e-mail has been sent.")},
            status=status.HTTP_200_OK,
        )

    @action(methods=["POST"], detail=False)
    def password_reset_confirm(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": _("Password has been reset.")},
            status=status.HTTP_200_OK,
        )

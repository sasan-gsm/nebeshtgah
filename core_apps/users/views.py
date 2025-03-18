from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.serializers import Serializer
from typing import List, Any, Type
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
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
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .repositories import UserRepository
from .permissions import IsOwnerOrReadOnly
from django.contrib.auth import get_user_model

User = get_user_model()


class UserViewSet(viewsets.GenericViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    repository = UserRepository

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.repository.get_all_users()
        return self.repository.get_by_id(id=self.request.user.id)

    def get_permissions(self) -> List[Any]:
        if action in ("register", "login", "password_reset", "password_reset_confirm"):
            return [AllowAny]
        return [IsAuthenticated]

    def get_serializer(self, *args, **kwargs) -> Type[Serializer]:
        return {
            "register": CustomRegisterSerializer,
            "login": CustomLoginSerializer,
            "password_reset": PasswordResetSerializer,
            "password_reset_confirm": PasswordResetConfirmSerializer,
        }.get(self.action, UserProfileSerializer)

    def get_object(self) -> User:  # type: ignore
        return self.repository.get_user_with_profile(self.kwargs.get("pk"))

    @action(methods=["POST"], detail=False)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request)
        return Response(status=status.HTTP_201_CREATED)

    @action(methods="POST")
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
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

    @method_decorator(cache_page(60 * 5))
    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request: Request) -> Response:
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

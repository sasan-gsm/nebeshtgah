from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.serializers import Serializer
from typing import Optional, List, Any, Type
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
from .permissions import IsOwnerOrReadOnly
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .repositories import UserRepository
from django.core.cache import cache
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
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
        user_id = self.kwargs.get("pk")
        if user_id is None:
            return self.request.user

        cache_key = f"user_profile_{user_id}"
        user = cache.get(cache_key)

        if not user:
            user = self.repository.get_user_with_profile(self.kwargs.get("pk"))
            if user:
                # Cache for 5 minutes
                cache.set(cache_key, user, timeout=60 * 5)
        return user

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
        # Clear user-specific cache
        if request.user.is_authenticated:
            cache.delete(f"user_profile_{request.user.id}")
            cache.delete(f"user_{request.user.id}")
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

    @action(methods=["POST"], detail=False, permission_classes=[IsAuthenticated])
    def password_change(self, request: Request) -> Response:
        """
        Change a user's password.

        Args:
            request: The request object

        Returns:
            Response: HTTP 200 OK on success
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Clear user cache after password change
        cache.delete(f"user_profile_{request.user.id}")
        cache.delete(f"user_{request.user.id}")

        return Response(
            {"detail": _("Password has been changed.")},
            status=status.HTTP_200_OK,
        )

    # Cache the response for 5 minutes, but vary by user
    @method_decorator(cache_page(60 * 5))
    @method_decorator(vary_on_cookie)
    @method_decorator(vary_on_headers("Authorization"))
    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request: Request) -> Response:
        """
        Get the current user's profile.

        Args:
            request: The request object

        Returns:
            Response: User profile data
        """
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @method_decorator(cache_page(60 * 5))
    @method_decorator(vary_on_headers("Authorization"))
    @action(methods=["GET"], detail=True, permission_classes=[IsAuthenticated])
    def profile(self, request: Request, pk: Optional[int] = None) -> Response:
        """
        Get a user's profile.

        Args:
            request: The request object
            pk: The user ID

        Returns:
            Response: User profile data
        """
        user = self.get_object()
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    @action(
        methods=["PUT", "PATCH"], detail=True, permission_classes=[IsOwnerOrReadOnly]
    )
    def update_profile(self, request: Request, pk: Optional[int] = None) -> Response:
        """
        Update a user's profile.

        Args:
            request: The request object
            pk: The user ID

        Returns:
            Response: Updated user profile data
        """
        user = self.get_object()
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Invalidate cache
        cache.delete(f"user_profile_{user.id}")
        cache.delete(f"user_{user.id}")

        return Response(serializer.data)

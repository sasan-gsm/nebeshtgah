from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView
from typing import Any


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Now supports checking foreign key ownership.
    """

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """Grant read access to all, but write access only to the owner."""
        if request.method in permissions.SAFE_METHODS:
            return True

        # If the object has a `user` attribute (for foreign key ownership)
        if hasattr(obj, "user"):
            return obj.user == request.user

        # Otherwise, assume direct ownership via `id`
        return getattr(obj, "id", None) == request.user.id

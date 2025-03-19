from django.core.cache import cache
from .models import User
from typing import Any, Optional, List, Protocol
from django.db import transaction
from loguru import logger
import json


class UserRepositoryProtocol(Protocol):
    def create_user(self, **kwargs) -> User: ...

    def get_by_id(self, id: int) -> Optional[User]: ...

    def update_user(self, user: User, user_data: dict[str:Any]) -> User: ...

    def delete_user(self, id: int) -> bool: ...

    def list_users(self, **filters: Any) -> dict[Optional[list], bool]: ...

    def get_user_with_profile(user_id: int) -> Optional[User]: ...

    def get_user_with_followers(user_id: int) -> Optional[User]: ...


class UserRepository:
    def create_user(self, **kwargs) -> User:
        return User.objects.create_user(**kwargs)

    def get_by_id(self, user_id: int) -> Optional[User]:
        cache_key = f"user_{user_id}"
        user = cache.get(cache_key)

        if not user:
            user = User.objects.filter(id=user_id).first()
            if user:
                cache.set(cache_key, user, timeout=60 * 5)  # Cache for 5 min
        return user

    def get_all_users(self) -> List[User]:
        cache_key = "all_users"
        users = cache.get(cache_key)
        if users is None:
            users = list(User.objects.all())
            if len(users) < 1000:
                cache.set(cache_key, users, timeout=60 * 5)  # 5 minutes
        return users

    def update_user(self, user: User, user_data: dict[str:Any]) -> User:
        with transaction.atomic():
            if "password" in user_data:
                user.set_password(user_data.pop("password"))

            [setattr(user, key, value) for key, value in user_data.items()]
            user.save()
            cache.delete(f"user_{user.id}")
            cache.delete("all_users")
            return user

    def delete_user(self, id: int) -> bool:
        try:
            User.objects.get(id=id).delete()
            return True

            cache.delete(f"user_{id}")
            cache.delete("all_users")
        except User.DoesNotExist:
            return False

    def list_users(self, **filters: Any) -> Optional[List[User]]:
        try:
            # Generate a cache key based on the filters
            cache_key = f"users_{json.dumps(filters, sort_keys=True)}"
            users = cache.get(cache_key)

            if not users:
                users = list(User.objects.filter(**filters))
                # Cache for 5 minutes, but only if the list is not too large
                if len(users) < 1000:
                    cache.set(cache_key, users, timeout=60 * 5)

            return users
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return None

    # Select related for reducing queries
    def get_user_with_profile(user_id: int) -> Optional[User]:
        cache_key = f"user_with_profile_{user_id}"
        user = cache.get(cache_key)

        if not user:
            user = User.objects.select_related("profile").filter(id=user_id).first()
            if user:
                # Cache for 5 minutes
                cache.set(cache_key, user, timeout=60 * 5)

        return user

    # Prefetch related for many-to-many relationships
    def get_user_with_followers(user_id: int) -> Optional[User]:
        return User.objects.prefetch_related("follow").filter(id=user_id).first()

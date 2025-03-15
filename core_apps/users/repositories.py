from .models import User
from django.core.exceptions import ObjectDoesNotExist
from typing import Any, Optional, Protocol
from django.db import transaction
from loguru import logger


class UserRepositoryProtocol(Protocol):
    def create_user(self, **kwargs) -> User: ...

    def get_by_id(self, id: int) -> Optional[User]: ...

    def update_user(self, user: User, user_data: dict[str:Any]) -> User: ...

    def delete_user(self, id: int) -> bool: ...


class UserRepository:
    def create_user(self, **kwargs) -> User:
        return User.objects.create_user(**kwargs)

    def get_by_id(self, id: int) -> Optional[User]:
        try:
            return User.objects.get(id=id)
        except ObjectDoesNotExist:
            return None

    def update_user(self, user: User, user_data: dict[str:Any]) -> User:
        with transaction.atomic():
            if "password" in user_data:
                user.set_password(user_data.pop("password"))

            [setattr(user, key, value) for key, value in user_data.items()]
            user.save()
            return user

    def delete_user(self, id: int) -> bool:
        try:
            User.objects.get(id=id).delete()
            return True
        except User.DoesNotExist:
            return False

    def list_user(self, **filters: Any) -> dict[Optional[list], bool]:
        try:
            User.objects.filter(**filters)
            return True
        except Exception as e:
            logger.error(e)
            return False

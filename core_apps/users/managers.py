from django.contrib.auth.models import BaseUserManager
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from typing import Any


class CustomUserManager(BaseUserManager):
    def _create_user(
        self, username: str, email: str, password=None, **kwargs: Any
    ) -> str:
        if not email:
            raise ValueError(_("The Email must be set"))
        if not username:
            raise ValueError(_("The Username must be set"))

        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_("Invalid email address"))

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, username: str, email: str, password=None, **kwargs: Any
    ) -> str:
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_active", True)

        if kwargs.get("is_staff") is not True:
            raise ValueError(_("must be staff."))
        if kwargs.get("is_superuser") is not True:
            raise ValueError(_("must be superuser."))

        return self._create_user(username, email, password, **kwargs)

    def create_user(self, username: str, email: str, password, **kwargs: Any) -> str:
        return self._create_user(username, email, password, **kwargs)

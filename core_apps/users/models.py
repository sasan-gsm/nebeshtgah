from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True, null=False)
    first_name = models.CharField(verbose_name=_("First Name"), max_length=30)
    last_name = models.CharField(verbose_name=_("Last Name"), max_length=30)
    email = models.EmailField(
        _("User Email Address"), max_length=60, unique=True, null=False
    )
    is_staff = models.BooleanField(default=False, null=False)
    is_active = models.BooleanField(default=True, null=False)
    is_superuser = models.BooleanField(default=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(_("last login"), blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    class Meta:
        db_table = "user"
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_username_or_email(self):
        return self.email if "@" in self.username else self.username

    def __str__(self):
        return f"Username: {self.username} - Email: {self.email}"

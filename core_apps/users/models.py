from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .managers import CustomUserManager


class User(AbstractBaseUser):
    username = models.CharField(max_length=30, unique=True, null=False)
    email = models.EmailField(
        _("User Email Address"), max_length=60, unique=True, null=False
    )
    created_at = models.DateTimeField(auto_now_add=timezone.now())
    updated_at = models.DateTimeField(auto_now=timezone.now())

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    class Meta:
        db_table = "users"
        verbose_name = _("User")
        verbose_name_plural = _("User")

    def __str__(self):
        return f"Username: {self.username} - Email: {self.email}"

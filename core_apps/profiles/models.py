from django.db import models
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField
from core_apps.common.models import BaseTimeStampModel
from django.utils.translation import gettext_lazy as _


User = get_user_model()


class Profile(BaseTimeStampModel):
    class Gender(models.TextChoices):
        MALE = "male", _("Male")
        FEMALE = "female", _("Female")

    avatar = models.ImageField(
        verbose_name=_("Profile Photo"), default="/profile_default.png"
    )
    phone_number = PhoneNumberField(
        verbose_name=_("Phone Number"), max_length=12, blank=True
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField(
        "self", symmetrical=False, related_name="following", blank=True
    )

    class Meta:
        db_table = "profile"

    def __str__(self):
        return f"{self.user.username}'s Profile"

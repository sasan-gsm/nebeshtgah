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
    gender = models.CharField(  # Added missing gender field
        max_length=10,
        choices=Gender.choices,
        default=Gender.MALE,
        verbose_name=_("Gender"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follower_count = models.PositiveIntegerField(
        verbose_name=_("Number of Followers"), default=0
    )

    class Meta:
        db_table = "profile"

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Follow(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "followed")
        db_table = "follow"

    def __str__(self) -> str:
        return f"{self.follower.username} follows {self.followed.username}"

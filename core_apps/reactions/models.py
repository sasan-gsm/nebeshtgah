from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth import get_user_model

User = get_user_model()


class Like(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    ContentType = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("ContentType", "object_id")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "like"
        verbose_name = _("Like")
        verbose_name_plural = _("Likes")
        unique_together = ["article", "user"]

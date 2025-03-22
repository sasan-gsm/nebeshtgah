from django.db import models
from core_apps.common.models import CommentableMixin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class Comment(models.Model, CommentableMixin):
    title = models.CharField(max_length=200)
    body = models.TextField(editable=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, verbose_name="Content Type"
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    like_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "comment"
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        ordering = ["-created_at"]
        indexes = models.Index(fields=["content_type", "object_id"])

    def get_like_count(self):
        from django.contrib.contenttypes.models import ContentType
        from core_apps.reactions.models import Like

        content_type = ContentType.objects.get_for_model(self)
        return Like.objects.filter(content_type=content_type, object_id=self.id).count()

    def __str__(self) -> str:
        return f"Comment by {self.author.username} on {self.article.title}"

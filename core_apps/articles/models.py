from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from core_apps.comments.models import Comment
from core_apps.common.models import CommentableMixin

User = get_user_model()


class Article(models.Model, CommentableMixin):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        PUBLISHED = "published", _("Published")

    title = models.CharField(
        max_length=255,
        verbose_name=_("Article Title"),
        unique=True,
        null=False,
        editable=True,
    )
    body = models.TextField(verbose_name=_("Article Body"), blank=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_("Article Status"),
    )
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    comments = GenericRelation(Comment)
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="articles", null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "article"
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        ordering = ["-created_at"]

    def increment_view_count(self) -> None:
        from django.db.models import F

        self.view_count = F("view_count") + 1
        self.save()
        self.refresh_from_db()

    def get_like_count(self):
        return self.like_count.count()

    def __str__(self) -> str:
        return self.title


class Author(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="author", verbose_name=_("User")
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="author",
        verbose_name=_("Article"),
    )

    class Meta:
        db_table = "author"
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")
        unique_together = ["user", "article"]

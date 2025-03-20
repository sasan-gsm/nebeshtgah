from django.db import models
from django.utils.translation import gettext_lazy as _
from core_apps.articles.models import Article


class Tag(models.Model):
    tag: str = models.CharField(
        max_length=128, verbose_name=_("Tag"), unique=True, null=False
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tag"
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self) -> str:
        return self.tag


class TagedItem(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="tagged_items"
    )
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="items")

    class Meta:
        db_table = "tagged_item"
        verbose_name = _("Tagged Item")
        verbose_name_plural = _("Tagged Items")
        unique_together = ["article", "tag"]

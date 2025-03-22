from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from core_apps.comments.models import Comment

User = get_user_model()


class BaseTimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CommentableMixin(models.Model):
    comments = GenericRelation(Comment)

    class Meta:
        abstract = True

    def add_comment(self, user: User, title: str, body: str, parent=None):
        return Comment.objects.create(
            user=user,
            title=title,
            body=body,
            parent=parent,
            content_object=self,
        )

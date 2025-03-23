from typing import Optional, List, Dict, Any, QuerySet, Protocol
from .models import Comment
from loguru import logger
from django.contrib.auth import get_user_model

User = get_user_model()


class CommentRepositoryProtocol(Protocol):
    def get_author_profile(self) -> User: ...

    def create_comment(self, data: Dict[str, Any], user: User) -> Comment: ...

    def update_comment(self, article: Comment, data: Dict[str, Any]) -> Comment: ...

    def list_articles(self, filters: Dict[str, Any] = None) -> QuerySet[Comment]: ...

    def delete_article(self, article: Comment) -> bool: ...


class CommentRepository:
    def get_author_profile(self, user: User) -> User:
        return Comment.objects.get(user=user)

    def create_comment(self, data: Dict[str, Any], user: User) -> Comment:
        return Comment.objects.create(**data)

    def update_comment(self, article: Comment, data: Dict[str, Any]) -> Comment:
        try:
            return Comment.objects.update(article)
        except Exception as e:
            logger.error(
                f"Article update error: {e}"
            )  # Log the error message to the console
            return None

    def list_articles(self, filters: Dict[str, Any] = None) -> QuerySet[Comment]:
        try:
            return Comment.objects.filter(**filters)
        except Exception as e:
            logger.error(
                f"Article list error: {e}"
            )  # Log the error message to the console
            return Comment.objects.none()

    def delete_article(self, article: Comment) -> bool:
        try:
            article.delete()
            return True
        except Exception as e:
            logger.error(
                f"Article delete error: {e}"
            )  # Log the error message to the console
            return False

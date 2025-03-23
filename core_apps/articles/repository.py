from typing import Optional, List, Dict, Any, QuerySet, Protocol
from .models import Article
from loguru import logger
from django.contrib.auth import get_user_model

User = get_user_model()


class ArticleRepositoryProtocol(Protocol):
    def get_article_by_id(self) -> Optional[Article]: ...

    def get_author_profile(self) -> User: ...

    def create_article(self, data: Dict[str, Any], user: User) -> Article: ...

    def update_article(self, article: Article, data: Dict[str, Any]) -> Article: ...

    def list_articles(self, filters: Dict[str, Any] = None) -> QuerySet[Article]: ...

    def delete_article(self, article: Article) -> bool: ...


class ArticleRepository:
    def get_article_by_id(self, article: Article) -> List[Article]:
        try:
            return Article.objects.get(id=article.id)
        except Article.DoesNotExist:
            logger.error(f"Article with id {article.id} does not exist")
            return None

    def get_author_profile(self) -> User:
        return

    def create_article(self, data: Dict[str, Any], user: User) -> Optional[Article]:
        try:
            return Article.objects.create(**data)
        except Exception as e:
            logger.error(
                f"Article creation error: {e}"
            )  # Log the error message to the console
            return None

    def update_article(self, article: Article, data: Dict[str, Any]) -> Article:
        try:
            return Article.objects.update(article)
        except Exception as e:
            logger.error(
                f"Article update error: {e}"
            )  # Log the error message to the console
            return None

    def list_articles(self, filters: Dict[str, Any] = None) -> QuerySet[Article]:
        return Article.objects.filter(**filters)

    def delete_article(self, article: Article) -> bool:
        try:
            article.delete()
            return True
        except Exception as e:
            logger.error(
                f"Article deletion error: {e}"
            )  # Log the error message to the console
            return False

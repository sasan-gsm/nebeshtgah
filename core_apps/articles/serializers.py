from rest_framework import serializers
from core_apps.tags.models import Tag
from core_apps.comments.models import Comment
from .models import Article, Author
from django.contrib.auth import get_user_model
from typing import Any, Dict, List

User = get_user_model()


class ArticleCreateSerializer(serializers.Serializer):
    tags = serializers.SlugRelatedField(
        many=True, slug_field="tag", queryset=Tag.objects.all(), required=False
    )

    class Meta:
        model = Article
        fields = ("title", "body", "status", "slug", "tags")

    def create(self, validated_data: Dict[str, Any]) -> Article:
        tags_data = validated_data.pop("tags", [])
        article = Article.objects.create(**validated_data)
        [article.tags.add(tag) for tag in tags_data]

        Author.objects.create(article=article, author=self.context["request"].user)
        return article


class ArticleUpdateSerializer(serializers.Serializer):
    tags = serializers.SlugRelatedField(
        many=True, slug_field="tag", queryset=Tag.objects.all(), required=False
    )
    authors = serializers.SerializerMethodField(read_only=True)

    author_usernames = serializers.SlugRelatedField(
        many=True,
        slug_field="username",
        queryset=User.objects.all(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Article
        fields = (
            "title",
            "body",
            "status",
            "slug",
            "tags",
            "authors",
            "author_usernames",
        )

    def get_authors(self, obj: Article) -> List[str]:
        return list(map(lambda author: author.user.full_name, obj.authors.all()))

    def update(self, instance: Article, validated_data):
        tags_data = validated_data.pop("tags", None)
        authors_data = validated_data.pop("author_usernames", None)
        # Update the article fields
        instance.__dict__.update(validated_data)
        instance.save()

        # Update tags using functional approach
        if tags_data:
            instance.tagged_items.all().delete()
            list(map(lambda tag: instance.tagged_items.create(tag=tag), tags_data))
        # Update authors using functional approach
        if authors_data:
            Author.objects.filter(article=instance).delete()
            list(map(lambda user: Author.create(user=user), authors_data))

        return instance


class ArticleListSerializer(serializers.Serializer):
    tags = serializers.SerializerMethodField(read_only=True)
    authors = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Article
        fields = (
            "id",
            "title",
            "tags",
            "authors",
            "status",
            "like_count",
            "updated_at",
        )

    def get_authors(self, obj: Article):
        return list(map(lambda author: author.user.full_name, obj.authors.all()))

    def get_tags(self, obj: Article):
        return list(map(lambda tag: tag.tag, obj.tagged_items.all()))


class ArticleDetailSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField(read_only=True)
    authors = serializers.SerializerMethodField(read_only=True)
    comments = serializers.SerializerMethodField(read_only=True)
    comments_likes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Article
        fields = (
            "id",
            "title",
            "body",
            "tags",
            "authors",
            "updated_at",
            "status",
            "created_at",
            "comments",
            "like_count",
            "comments_likes",
            "view_count",
        )

    def get_authors(self, obj: Article):
        return list(map(lambda author: author.user.full_name, obj.authors.all()))

    def get_tags(self, obj: Article):
        return list(map(lambda tag: tag.tag, obj.tagged_items.all()))

    def get_comments(self, obj: Article) -> List[Dict[str, Any]]:
        from core_apps.comments.serializers import CommentSerializer

        comments = obj.comments.all()
        return CommentSerializer(comments, many=True).data

    def get_comments_likes(self, obj: Comment):
        return sum(comment.like_count for comment in obj.comments.all())

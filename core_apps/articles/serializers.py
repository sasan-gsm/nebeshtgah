from rest_framework import serializers
from django.db import transaction
from core_apps.tags.models import Tag
from django.utils.text import slugify
from core_apps.comments.models import Comment
from .models import Article, Author
from django.contrib.auth import get_user_model
from typing import Any, Dict, List

User = get_user_model()


class ArticleCreateSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True, slug_field="tag", queryset=Tag.objects.all(), required=False
    )

    class Meta:
        model = Article
        fields = ("title", "body", "status", "slug", "tags")

    def create(self, validated_data: Dict[str, Any]) -> Article:
        tags_data = validated_data.pop("tags", [])
        article = super().create(**validated_data)
        article.tags.set(tags_data)

        Author.objects.create(article=article, author=self.context["request"].user)
        return article


class ArticleUpdateSerializer(serializers.ModelSerializer):
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
        with transaction.atomic():
            tags_data = validated_data.pop("tags", None)
            authors_data = validated_data.pop("author_usernames", None)

            # Update the article fields
            [setattr(instance, key, value) for key, value in validated_data.items()]
            # Dynamically update slug
            [
                validated_data.update(
                    {"slug": slugify(validated_data["title"], allow_unicode=True)}
                )
                if "title" in validated_data
                and validated_data["title"] != instance.title
                else None
            ]
            instance.save()

            # Update tags using functional approach
            if tags_data:
                instance.tags.set(tags_data)
            # Update authors using functional approach
            if authors_data:
                instance.authors.set(authors_data)

        return instance


class ArticleListSerializer(serializers.ModelSerializer):
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
        return obj.authors.values_list("user__full_name", flat=True)

    def get_tags(self, obj: Article):
        return obj.tagged_items.values_list("tag__tag", flat=True)


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
        return obj.authors.values_list("user__full_name", flat=True)

    def get_tags(self, obj: Article):
        return obj.tagged_items.values_list("tag__tag", flat=True)

    def get_comments(self, obj: Article):
        return obj.comments.values(
            "id", "title", "body", "user__full_name", "created_at", "updated_at"
        )

    def get_comments_likes(self, obj: Comment):
        return sum(comment.like_count for comment in obj.comments.all())

from rest_framework import serializers
from .models import Profile, Follow
from django.contrib.auth import get_user_model


User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    followers_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ("user", "phone_number", "gender", "avatar", "followers_count")

    def get_followers_count(self, obj: Profile) -> int:
        return obj.user.follower.count()


class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.PrimaryKeyRelatedField(read_only=True)
    followed = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Follow
        fields = (
            "follower",
            "followed",
        )
        extra_kwargs = {"created_at": {"read_only": True}}

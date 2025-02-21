from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    followers_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ("user", "phone_number", "gender", "avatar", "followers_count")

    def get_followers_count(self, obj: Profile) -> int:
        return obj.followers.count()

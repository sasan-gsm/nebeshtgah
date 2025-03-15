from .repositories import ProfileRepositoryProtocol, FollowRepositoryProtocol
from django.contrib.auth import get_user_model
from loguru import logger

User = get_user_model()


class ProfileService:
    def __init__(self, profile_repo: ProfileRepositoryProtocol):
        self.profile_repo = profile_repo

    def get_profile(self, id: int, **kwargs):
        return self.profile_repo.get_by_user(user=id)


class FollowService:
    def __init__(self, follow_repo: FollowRepositoryProtocol):
        self.follow_repo = follow_repo

    def follow_user(self, follower: User, followed: User):  # type: ignore
        self.follow_repo.follow(follower=follower, followed=followed)
        return True, "Successful."

    def unfollow_user(self, follower: User, followed: User):  # type: ignore
        self.follow_repo.unfollow(follower=follower, followed=followed)
        return True, "Successful."

from django.db import DatabaseError
from typing import Tuple, Optional, Protocol
from django.contrib.auth import get_user_model
from .models import Profile, Follow
from loguru import logger

User = get_user_model()


class ProfileRepositoryProtocol(Protocol):
    def get_by_user(self, user) -> Profile: ...


class ProfileRepository:
    def get_by_user(self, user) -> Profile:
        return Profile.objects.get(user=user)

    def create_profile(self, profile: Profile) -> bool:
        try:
            profile.objects.create(profile)
            return True
        except Exception as e:
            logger.error(f"Profile creation error: {e}")
            return False


class FollowRepositoryProtocol(Protocol):
    def follow(self, follower: User, followed: User) -> Tuple[bool, Optional(str)]: ...  # type: ignore

    def unfollow(
        self,
        follower: User,  # type: ignore
        followed: User,  # type: ignore
    ) -> Tuple[bool, Optional(str)]: ...  # type: ignore


class FollowRepository:
    def follow(self, follower: User, followed: User) -> Tuple[bool, Optional(str)]:  # type: ignore
        try:
            if follower == followed:
                return False
            follow, created = Follow.objects.get_or_create(
                follower=follower, followed=followed
            )
            if not created:
                return False, "already following"
            return True

        except DatabaseError as e:
            return False, f"{e}"
        except Exception as e:
            return False, f"{e}"

    def unfollow(self, follower: User, followed: User) -> Tuple[bool, Optional(str)]:  # type: ignore
        try:
            delete, _ = Follow.objects.filter(
                follower=follower, followed=followed
            ).delete()
            if not delete:
                return False
            return True, "Successfully unfollowed user"

        except DatabaseError as e:
            return False, f"{e}"
        except Exception as e:
            return False, f"{e}"

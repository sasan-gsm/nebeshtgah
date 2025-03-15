from .repositories import UserRepositoryProtocol
from typing import Dict, Any


class UserService:
    def __init__(self, user_repo: UserRepositoryProtocol):
        self.user_repo = user_repo

    def create_user(self, user_data: Dict[str, Any]):
        user = self.user_repo.create_user(user_data)
        return user

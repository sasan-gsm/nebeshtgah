from .repositories import UserRepositoryProtocol
from typing import Optional, Dict, Any
from .models import User


class UserService:
    def __init__(self, user_repo: UserRepositoryProtocol):
        self.user_repo = user_repo

    def create_user(self, user_data: Dict[str, Any]):
        user = self.user_repo.create_user(user_data)
        return user

    def get_user(self, user_id: int) -> Optional[User]:
        return self.user_repo.get_by_id(user_id)

    def update_user(self, user: User, user_data: Dict[str, Any]) -> User:
        return self.user_repo.update_user(user, user_data)

    def delete_user(self, user_id: int) -> bool:
        return self.user_repo.delete_user(user_id)

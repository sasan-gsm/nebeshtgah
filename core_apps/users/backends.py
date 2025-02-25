from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from loguru import logger

User = get_user_model()

class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, login=None, username=None, password=None, **kwargs):
        logger.info(f"Raw: Login={login}, Username={username}, Password={password}, Kwargs={kwargs}")
        auth_value = login or username or kwargs.get("username") or request.POST.get("username")
        logger.info(f"Resolved Auth Value: {auth_value}")
        if auth_value is None:
            logger.warning("Auth value is None - all sources failed")
            return None

        if "@" in auth_value:
            user = User.objects.filter(email=auth_value).first()
        else:
            user = User.objects.filter(username=auth_value).first()
        if user and user.check_password(password):
            logger.info(f"Authenticated user: {user.username}")
            return user if self.user_can_authenticate(user) else None
        logger.warning(f"No user found for {auth_value}")
        return None
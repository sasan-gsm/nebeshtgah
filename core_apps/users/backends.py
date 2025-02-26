from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
import re

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    @staticmethod
    def is_valid_email(value):
        # Regex for email validation
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return re.match(email_regex, value) is not None

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Use the `username` parameter for both email and username authentication
        auth_value = username or request.POST.get("username")

        # Check if the auth_value is an email or username
        if self.is_valid_email(auth_value):
            user = User.objects.filter(email=auth_value).first()
        else:
            user = User.objects.filter(username=auth_value).first()

        # Verify the password and return the user if valid
        if user and user.check_password(password):
            return user if self.user_can_authenticate(user) else None

        return None

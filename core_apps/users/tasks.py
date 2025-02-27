from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task
def send_password_reset_email(user_id: int, reset_url: str) -> None:
    user = User.objects.get(id=user_id)
    subject = "Password Reset Request"
    message = render_to_string(
        "registration/password_reset_email.html",
        {"user": user, "reset_url": reset_url},
    )
    send_mail(subject, message, "noreply@example.com", [user.email])

from django.dispatch import Signal, receiver
from django.utils import timezone

user_login_signal = Signal()


@receiver(user_login_signal)
def update_user_last_login(sender, instance, request, **kwargs):
    instance.last_login = timezone.now()
    instance.save(update_fields=["last_login"])

from django.urls import path, include
from .views import PasswordResetView, PasswordResetConfirmView

urlpatterns = [
    path("auth/", include("dj_rest_auth.urls")),
    path(
        "auth/token/refresh/",
        include("rest_framework_simplejwt.views.TokenRefreshView"),
    ),
    path("password/reset/", PasswordResetView.as_view(), name="password-reset"),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
]

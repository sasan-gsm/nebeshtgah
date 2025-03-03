from django.urls import path, include
from .views import CustomPasswordResetView, CustomPasswordResetConfirmView

urlpatterns = [
    path("auth/", include("dj_rest_auth.urls")),
    path(
        "auth/token/refresh/",
        include("rest_framework_simplejwt.views.TokenRefreshView"),
    ),
    path("password/reset/", CustomPasswordResetView.as_view(), name="password-reset"),
    path(
        "password/reset/confirm/",
        CustomPasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
]

from django.urls import path, include

urlpatterns = [
    path("auth/", include("dj_rest_auth.urls")),
    path(
        "auth/token/refresh/",
        include("rest_framework_simplejwt.views.TokenRefreshView"),
    ),
]

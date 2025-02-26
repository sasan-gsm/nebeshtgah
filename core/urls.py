from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    # path("accounts/", include("allauth.urls")),  # Allauth URLs
]

# if settings.DEBUG:
#     import debug_toolbar

#     urlpatterns = [
#         path("__debug__/", include(debug_toolbar.urls)),  # Add Debug Toolbar URLs
#     ] + urlpatterns

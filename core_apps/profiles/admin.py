from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin):
    model = Profile

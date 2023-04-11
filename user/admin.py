from django.contrib import admin

from .models import UserModel


@admin.register(UserModel)
class UserAdmin(admin.ModelAdmin):
    """
    Admin panel: User

    """
    list_display = ["id", "username"]
from django.contrib import admin

from .models import Card


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    """
    Admin panel: Card

    """
    list_display = ["id", "description", "status", "is_deleted"]

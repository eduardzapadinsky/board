from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from .models import Card


class CardListView(LoginRequiredMixin, ListView):
    model = Card

    def get_context_data(self, *args, **kwargs):
        """
        Add list of cards from Card model

        """
        card_list_status = Card.STATUS_CHOICES
        context = super().get_context_data(*args, **kwargs)
        context["card_list_status"] = card_list_status
        return context

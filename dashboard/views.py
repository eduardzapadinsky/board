from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import ListView

from .models import Card

CARD_LIST_STATUS = Card.STATUS_CHOICES


class CardListView(LoginRequiredMixin, ListView):
    model = Card

    def get_context_data(self, *args, **kwargs):
        """
        Add list of cards from Card model

        """
        context = super().get_context_data(*args, **kwargs)
        context["card_list_status"] = CARD_LIST_STATUS
        return context


def card_move(pk):
    card = Card.objects.get(id=pk)
    card_status = card.status
    card_list_status_name = [i[0] for i in CARD_LIST_STATUS]
    card_status_index = card_list_status_name.index(card_status)
    return card, card_list_status_name, card_status_index


def card_move_left(request, pk):
    card, card_list_status_name, card_status_index = card_move(pk)
    if card_status_index != 0:
        next_cart_status = card_list_status_name[card_status_index - 1]
        card.status = next_cart_status
        card.save()
    return redirect("dashboard:board")


def card_move_right(request, pk, *args):
    card, card_list_status_name, card_status_index = card_move(pk)
    if card_status_index != len(card_list_status_name) - 1:
        next_cart_status = card_list_status_name[card_status_index + 1]
        card.status = next_cart_status
        card.save()
    return redirect("dashboard:board")

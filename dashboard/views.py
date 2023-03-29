from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView

from user.models import UserModel
from .models import Card
from .forms import CardForm

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


class CardCreateView(LoginRequiredMixin, CreateView):
    form_class = CardForm
    template_name = "dashboard/card_form.html"

    def post(self, request, *args, **kwargs):
        form = CardForm(request.POST)
        creator = UserModel.objects.get(id=request.user.id)

        if form.is_valid():
            cd = form.cleaned_data
            description = cd["description"]
            executor = cd["executor"]
            Card.objects.update_or_create(
                creator=creator,
                description=description,
                executor=executor
            )
        return redirect("dashboard:card-create")

    def get_success_url(self):
        return redirect("dashboard:board")


class CardUpdateView(UpdateView):
    """
    ToDo

    """
    model = Card
    form_class = CardForm
    template_name = "dashboard/card_form.html"

    def get_success_url(self):
        return reverse("dashboard:board")

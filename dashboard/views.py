from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core.exceptions import PermissionDenied

from user.models import UserModel
from .models import Card
from .forms import CardForm, CardFormSuperuser

CARD_LIST_STATUS = Card.STATUS_CHOICES


class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Superuser-only permission
    """

    def test_func(self):
        return self.request.user.is_superuser


class SuperuserRestrictedMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Deny permission for superuser
    """

    def test_func(self):
        return not self.request.user.is_superuser


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
    return card, card_status, card_list_status_name, card_status_index


def card_move_left(request, pk):
    card, card_status, card_list_status_name, card_status_index = card_move(pk)
    if card_status not in [
        "New", "Done"
    ] and card.executor == request.user or card_status == "Done" and request.user.is_superuser:
        next_cart_status = card_list_status_name[card_status_index - 1]
        card.status = next_cart_status
        card.save()
    return redirect("dashboard:board")


def card_move_right(request, pk, *args):
    card, card_status, card_list_status_name, card_status_index = card_move(pk)
    if card_status not in [
        "Ready", "Done"
    ] and card.executor == request.user or card_status == "Ready" and request.user.is_superuser:
        next_cart_status = card_list_status_name[card_status_index + 1]
        card.status = next_cart_status
        card.save()
    return redirect("dashboard:board")


class CardCreateView(SuperuserRestrictedMixin, LoginRequiredMixin, CreateView):
    form_class = CardForm
    template_name = "dashboard/card_form.html"

    def post(self, request, *args, **kwargs):
        form = CardForm(request.POST)
        creator = UserModel.objects.get(id=request.user.id)

        if form.is_valid():
            cd = form.cleaned_data
            description = cd["description"]
            executor_status = request.POST.get("executor", False)
            if executor_status:
                executor = creator
            else:
                executor = None
            Card.objects.update_or_create(
                creator=creator,
                description=description,
                executor=executor
            )
            return redirect("dashboard:board")
        else:
            return redirect("dashboard:card-create")

    def get_success_url(self):
        return redirect("dashboard:board")


class CardUpdateView(LoginRequiredMixin, UpdateView):
    model = Card
    form_class = CardForm
    template_name = "dashboard/card_form.html"

    def form_valid(self, form):
        creator = self.object.creator
        current_user = self.request.user
        if current_user == creator:
            executor_status = self.request.POST.get("executor", False)
            if executor_status:
                executor = creator
            else:
                executor = None
            form.instance.executor = executor
            return super().form_valid(form)
        else:
            raise PermissionDenied()

    def get_success_url(self):
        return reverse("dashboard:board")


class CardUpdateViewSuperuser(SuperuserRequiredMixin, UpdateView):
    model = Card
    form_class = CardFormSuperuser
    template_name = "dashboard/card_form.html"

    def get_success_url(self):
        return reverse("dashboard:board")


class CardDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Card
    success_url = reverse_lazy("dashboard:board")

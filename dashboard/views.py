from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core.exceptions import PermissionDenied
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user.models import UserModel
from .models import Card
from .forms import CardForm, CardFormSuperuser
from .serializers import CardSerializer
from .permissions import UserPermission, UserReadPermission

CARD_LIST_STATUS = Card.STATUS_CHOICES


class CardListViewAPI(viewsets.ModelViewSet):
    """
    Manage CRUD operations in REST

    """
    permission_classes = [IsAuthenticated, UserPermission]
    queryset = Card.objects.all()
    serializer_class = CardSerializer

    def perform_create(self, serializer):
        """
        Add user during the card creation

        """
        serializer.save(creator=self.request.user)

    @staticmethod
    def update_status():
        response_data = {
            'success': False,
            'message': "You can't change status, you are not an 'executor'"
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def update_status_done():
        response_data = {
            'success': False,
            'message': "Status can't be 'Done'"
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def update_status_some():
        response_data = {
            'success': False,
            'message': "Status can be only 'Ready' or 'Done'"
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def update_executor():
        response_data = {
            'success': False,
            'message': "Executor can't be other user"
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def update_without_executor():
        response_data = {
            'success': False,
            'message': "You can't change 'executor'"
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def update_description():
        response_data = {
            'success': False,
            'message': "You can't change 'description'"
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Permissions during card update

        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        current_user = self.request.user
        current_data = request.data
        if instance.creator == current_user and instance.executor == current_user:
            if current_data.get("status") == "Done":
                return self.update_status_done()
            elif current_data.get("executor") not in [None, current_user.id]:
                return self.update_executor()
        if instance.creator == current_user and instance.executor != current_user:
            if current_data.get("status"):
                return self.update_status()
            elif current_data.get("executor") not in [None, current_user.id]:
                return self.update_executor()
        if instance.executor == current_user and instance.creator != current_user:
            if current_data.get("status") == "Done":
                return self.update_status_done()
            elif current_data.get("description"):
                return self.update_description()
            elif current_data.get("executor"):
                return self.update_without_executor()
        if current_user.is_superuser:
            if current_data.get("status") not in ["Ready", "Done"]:
                return self.update_status_some()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response_data = {
            'success': True,
            'message': 'Object updated successfully'
        }
        return Response(response_data, status=status.HTTP_200_OK)


class CardDetailViewAPI(viewsets.ModelViewSet):
    """
    Show cards according to the status using REST

    """
    permission_classes = [IsAuthenticated, UserReadPermission]
    serializer_class = CardSerializer
    queryset = Card.objects.all()

    def get_queryset(self):
        """
        Filter cards according to there status

        """
        card_dict_status_name = {i[0].lower(): i[0] for i in CARD_LIST_STATUS}
        card_status = card_dict_status_name[self.kwargs["status"]]
        queryset = Card.objects.filter(status=card_status)
        return queryset


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
    """
    Base for moving card

    """
    card = Card.objects.get(id=pk)
    card_status = card.status
    card_list_status_name = [i[0] for i in CARD_LIST_STATUS]
    card_status_index = card_list_status_name.index(card_status)
    return card, card_status, card_list_status_name, card_status_index


def card_move_left(request, pk):
    """
    Moving card to the left status

    """
    card, card_status, card_list_status_name, card_status_index = card_move(pk)
    if card_status not in [
        "New", "Done"
    ] and card.executor == request.user or card_status == "Done" and request.user.is_superuser:
        next_cart_status = card_list_status_name[card_status_index - 1]
        card.status = next_cart_status
        card.save()
    return redirect("dashboard:board")


def card_move_right(request, pk, *args):
    """
    Moving card to the right status

    """
    card, card_status, card_list_status_name, card_status_index = card_move(pk)
    if card_status not in [
        "Ready", "Done"
    ] and card.executor == request.user or card_status == "Ready" and request.user.is_superuser:
        next_cart_status = card_list_status_name[card_status_index + 1]
        card.status = next_cart_status
        card.save()
    return redirect("dashboard:board")


class CardCreateView(SuperuserRestrictedMixin, LoginRequiredMixin, CreateView):
    """
    Creating card for common user

    """
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
    """
    Updating card for some fields by common user

    """
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
    """
    Updating card by superuser

    """
    model = Card
    form_class = CardFormSuperuser
    template_name = "dashboard/card_form.html"

    def get_success_url(self):
        return reverse("dashboard:board")


class CardDeleteView(SuperuserRequiredMixin, DeleteView):
    """
    Deleting card by superuser

    """
    model = Card
    success_url = reverse_lazy("dashboard:board")

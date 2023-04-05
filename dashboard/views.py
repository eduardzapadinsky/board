from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core.exceptions import PermissionDenied
from rest_framework import viewsets, status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user.models import UserModel
from .models import Card
from .forms import CardForm, CardFormSuperuser
from .serializers import CardSerializer
from .permissions import UserPermission, UserReadPermission

CARD_LIST_STATUS = Card.STATUS_CHOICES


# class CardListViewAPI(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated, UserPermission]
#     queryset = Card.objects.all()
#     serializer_class = CardSerializer
#
#     def perform_create(self, serializer):
#         serializer.save(creator=self.request.user)


class CardListViewAPI(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, UserPermission]
    queryset = Card.objects.all()
    serializer_class = CardSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        current_user = self.request.user
        current_data = request.data
        response_data = {}
        if instance.creator == current_user and instance.executor == current_user:
            if current_data.get("status") == "Done":
                response_data = {
                    'success': False,
                    'message': "Status can't be 'Done'"
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            elif current_data.get("executor"):
                if current_data.get("executor") != current_user:
                    response_data = {
                        'success': False,
                        'message': "Executor can't be other user"
                    }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        if instance.creator == current_user:
            if current_data.get("status"):
                response_data = {
                    'success': False,
                    'message': "You can't change status, you are not an 'executor'"
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            elif current_data.get("executor"):
                if current_data.get("executor") != current_user:
                    response_data = {
                        'success': False,
                        'message': "Executor can't be other user"
                    }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        if instance.executor == current_user:
            if current_data.get("status") == "Done":
                response_data = {
                    'success': False,
                    'message': "Status can't be 'Done'"
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            elif current_data.get("description"):
                response_data = {
                    'success': False,
                    'message': "You can't change 'description'"
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            elif current_data.get("executor"):
                response_data = {
                    'success': False,
                    'message': "You can't change 'executor'"
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        if current_user.is_superuser:
            if current_data.get("status"):
                if current_data.get("status") not in ["Ready", "Done"]:
                    response_data = {
                        'success': False,
                        'message': "Status can be only 'Ready' or 'Done'"
                    }
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response_data = {
            'success': True,
            'message': 'Object updated successfully'
        }
        return Response(response_data, status=status.HTTP_200_OK)


class CardDetailViewAPI(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, UserReadPermission]
    serializer_class = CardSerializer
    queryset = Card.objects.all()

    def get_queryset(self):
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

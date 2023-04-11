"""
Dashboard app URL Configuration

"""

from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('', views.CardDetailViewAPI)

app_name = "dashboard"
urlpatterns = [
    path("", views.CardListView.as_view(), name="homepage"),
    path("board/", views.CardListView.as_view(), name="board"),
    path("card/create/", views.CardCreateView.as_view(), name="card-create"),
    path("card/full-update/<int:pk>/", views.CardUpdateViewSuperuser.as_view(), name="card-full-update"),
    path("card/update/<int:pk>/", views.CardUpdateView.as_view(), name="card-update"),
    path("card/delete/<int:pk>/", views.CardDeleteView.as_view(), name="card-delete"),
    path("card/move_left/<int:pk>/", views.card_move_left, name="card-move-left"),
    path("card/move_right/<int:pk>/", views.card_move_right, name="card-move-right"),
    path("api/card/status/<str:status>/", include(router.urls)),
]

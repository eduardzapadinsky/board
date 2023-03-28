"""
Dashboard app URL Configuration

"""

from django.urls import path

from . import views

app_name = "dashboard"
urlpatterns = [
    path("", views.CardListView.as_view(), name="homepage"),
    path("board/", views.CardListView.as_view(), name="board"),
    path("card/move_left/<int:pk>/", views.card_move_left, name="card-move-left"),
    path("card/move_right/<int:pk>/", views.card_move_right, name="card-move-right"),
]

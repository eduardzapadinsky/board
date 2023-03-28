"""
Dashboard app URL Configuration

"""

from django.urls import path

from . import views

app_name = "dashboard"
urlpatterns = [
    path("", views.CardListView.as_view(), name="homepage"),
    path("board/", views.CardListView.as_view(), name="board"),
]

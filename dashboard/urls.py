"""
Dashboard app URL Configuration

"""

from django.urls import path

from . import views

app_name = "user"
urlpatterns = [
    path("", views.Logout.as_view(), name="logout"),
    path("board/", views.Logout.as_view(), name="logout"),
]

"""board URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken import views

from user.views import UserViewAPI
from dashboard.views import CardListViewAPI

# from .logout_middleware import CustomAuthToken


router = routers.DefaultRouter()
router.register("user", UserViewAPI)
router.register("card", CardListViewAPI)

urlpatterns = [
                  path("admin/", admin.site.urls),
                  path("", include("user.urls", namespace="user")),
                  path("", include("dashboard.urls", namespace="dashboard")),
                  # path('api/auth/', CustomAuthToken.as_view()),
                  path("api/auth/", views.obtain_auth_token),
                  path("api/", include(router.urls)),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""
URL configuration for inventory_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from .views import InventoryListView
from .views import UserRegistrationView
from rest_framework.authtoken.views import obtain_auth_token



urlpatterns = [
    path('api/items/', InventoryListView.as_view(), name='inventory-list'),
    path('api/items/create/', InventoryListView.as_view(), name='inventory-create'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),  # Route for getting the token

]

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
from django.urls import path
from .views import HomeView, LoginPageView, ProfileView, getInventoryListView, inventory_item_history, postInventoryListView
from .views import UserRegistrationView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import LogoutView
from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version='v1',
        description="My API description",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="Awesome License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

    

urlpatterns = [
    path('', HomeView, name='home'), # this is tested and works
    path('api/items/', getInventoryListView, name='inventory-list'), # this is tested and works
    path('api/items/create/', postInventoryListView, name='inventory-create'), # this is tested and works
    path('register/', UserRegistrationView, name='register'), # this is tested and works
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),  # Route for getting the token
    path('login/', LoginPageView, name='login'), # this is tested and works
    path('logout/', LogoutView, name='logout'), # this is tested and works
    path('profile/', ProfileView, name='profile'), # this is tested and works
    path('inventory/<int:pk>/', views.inventory_detail, name='inventory_detail'), # this is tested and works
    path('inventory/<int:item_id>/update_quantity/', views.update_quantity, name='update_quantity'), # this is tested and works
    path('change-log/', views.change_log, name='change_log'), # this is tested and works
    path('inventory/<int:item_id>/history/', inventory_item_history, name='inventory_item_history'), # this is tested and works

    # paths for ui generated documentation
    path('doc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]


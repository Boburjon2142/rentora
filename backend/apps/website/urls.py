from django.urls import path
from django.contrib.auth import views as auth_views

from .views import HomeView, PropertyListView, PropertyDetailView, PropertyCreateView, RegisterView, CabinetView

app_name = 'website'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('properties/', PropertyListView.as_view(), name='property_list'),
    path('properties/<int:pk>/', PropertyDetailView.as_view(), name='property_detail'),
    path('properties/new/', PropertyCreateView.as_view(), name='property_create'),
    path('cabinet/', CabinetView.as_view(), name='cabinet'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

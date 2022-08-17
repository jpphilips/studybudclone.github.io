from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_page, name='register'),

    path('', views.home, name='home'),
    path('room/<str:pk>/', views.room, name='room'),
    path('profile/<str:pk>/', views.user_profile, name='user-profile'),

    path('create-room', views.create_room, name='create-room'),
    path('update-room/<str:pk>/', views.update_room, name='update-room'),
    path('delete-room/<str:pk>/', views.delete_room, name='delete-room'),

    path('update-message/<str:pk>/', views.update_message, name='update-message'),
    path('delete-message/<str:pk>/', views.delete_message, name='delete-message'),

    path('edit-profile/', views.update_user, name='update-user'),
    path('settings/', views.settings, name='settings'),
]

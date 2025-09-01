# coding=utf-8
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path("login/discord/", views.discord_login_view, name='discord_login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path("password_change/", views.password_change_view, name='password_change'),
    path("sync_avatar/", views.sync_avatar_view, name="sync_avatar"),
]

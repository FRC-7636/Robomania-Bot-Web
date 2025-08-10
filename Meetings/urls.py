# coding=utf-8
from django.urls import path
from . import views

urlpatterns = [
    path("<int:meeting_id>/", views.index, name="meeting_info"),
    path("<int:meeting_id>/edit/", views.edit, name="meeting_edit"),
]

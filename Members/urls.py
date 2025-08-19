# coding=utf-8
from django.urls import path
from . import views

urlpatterns = [
    path("<int:member_id>/", views.info, name="member_info"),
    path("<int:member_id>/edit/", views.edit, name="member_edit"),
]

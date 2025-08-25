# coding=utf-8
from django.urls import path
from . import views

urlpatterns = [
    path("list/", views.list_members, name="member_list"),
    path("<int:member_id>/", views.info, name="member_info"),
    path("<int:member_id>/edit/", views.edit, name="member_edit"),
    path("<int:member_id>/edit_warning_points/", views.edit_warning_points, name="member_edit_warning_points"),
]

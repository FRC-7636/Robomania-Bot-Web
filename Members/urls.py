# coding=utf-8
from django.urls import path
from . import views

urlpatterns = [
    path("list/", views.list_members, name="member_list"),
    path("bulk_edit/", views.bulk_edit_members, name="member_bulk_edit"),
    path("<int:member_id>/", views.info, name="member_info"),
    path("<int:member_id>/edit/", views.edit, name="member_edit"),
    path("<int:member_id>/edit_warning_points/", views.edit_warning_points, name="member_edit_warning_points"),
    path("<int:member_id>/disable/", views.disable_member, name="member_disable"),
    path("<int:member_id>/enable/", views.enable_member, name="member_enable"),
]

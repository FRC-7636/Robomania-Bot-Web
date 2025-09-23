# coding=utf-8
from django.urls import path
from . import views

urlpatterns = [
    path("<int:announcement_id>/", views.index, name="announcement_info"),
    path("<int:announcement_id>/edit/", views.edit_view, name="announcement_edit"),
    path("<int:announcement_id>/delete/", views.delete_view, name="announcement_delete"),
    path("new/", views.create_view, name="announcement_new"),
    path("list/", views.list_view, name="announcement_list"),
]

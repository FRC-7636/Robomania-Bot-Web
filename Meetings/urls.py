# coding=utf-8
from django.urls import path
from . import views

urlpatterns = [
    path("<int:meeting_id>/", views.index, name="meeting_info"),
    path("<int:meeting_id>/edit/", views.edit, name="meeting_edit"),
    path("<int:meeting_id>/delete/", views.delete, name="meeting_delete"),
    path("<int:meeting_id>/submit_absent_request/", views.submit_absent_request, name="meeting_submit_absent"),
]

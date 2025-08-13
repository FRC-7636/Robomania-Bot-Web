# coding=utf-8
from django.urls import path
from . import views

urlpatterns = [
    path("new/", views.create, name="meeting_create"),
    path("<int:meeting_id>/", views.index, name="meeting_info"),
    path("<int:meeting_id>/edit/", views.edit, name="meeting_edit"),
    path("<int:meeting_id>/delete/", views.delete, name="meeting_delete"),
    path("<int:meeting_id>/submit_absent_request/", views.submit_absent_request, name="meeting_submit_absent"),
    path("<int:meeting_id>/review_absent_requests/", views.review_absent_requests_page, name="meeting_review_absents"),
    path(
        "<int:meeting_id>/review_absent_requests_api/",
        views.review_absent_requests_api,
        name="meeting_review_absents_api"
    ),
]

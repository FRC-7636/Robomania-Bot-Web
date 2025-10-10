# coding=utf-8
from django.urls import path
from . import views

urlpatterns = [
    path("new/", views.create, name="meeting_create"),
    path("list/", views.list_view, name="meeting_list"),
    path("<int:meeting_id>/", views.index, name="meeting_info"),
    path("<int:meeting_id>/edit/", views.edit, name="meeting_edit"),
    path("<int:meeting_id>/delete/", views.delete, name="meeting_delete"),
    path("<int:meeting_id>/sign_in/new/", views.sign_in_create_view, name="meeting_signin_create"),
    path("<int:meeting_id>/sign_in/<str:sign_in_uuid>/", views.sign_in_view, name="meeting_signin"),
    path("<int:meeting_id>/sign_in/<str:sign_in_uuid>/scan/", views.sign_in_scan_view, name="meeting_signin_scan"),
    path("<int:meeting_id>/submit_absent_request/", views.submit_absent_request, name="meeting_submit_absent"),
    path("<int:meeting_id>/review_absent_requests/", views.review_absent_requests_page, name="meeting_review_absents"),
    # path("tws/", views.test_ws, name="websocket_test"),
    path(
        "<int:meeting_id>/review_absent_requests_api/",
        views.review_absent_requests_api,
        name="meeting_review_absents_api"
    ),
]

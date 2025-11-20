# coding=utf-8
from django.urls import re_path, path
from . import views

urlpatterns = [
    re_path(r"^$", views.uploader_upload, name='uploader_upload'),
    path("mdimage/", views.mdimage_upload, name='mdimage_upload'),
]

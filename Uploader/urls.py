# coding=utf-8
from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r"^$", views.index, name='upload_index'),
    re_path(r"^$", views.uploader_upload, name='uploader_upload'),
]

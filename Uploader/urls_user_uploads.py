# coding=utf-8
from django.urls import path
from . import views

urlpatterns = [
    path("uploader/<str:uuid>/", views.uploader_download, name='uploader_download'),
    path("mdimages/<str:uuid>.webp", views.mdimage_download, name='mdimage_download'),
]

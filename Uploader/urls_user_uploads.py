# coding=utf-8
from django.urls import path
from . import views

urlpatterns = [
    path("/uploader/<str:uuid>", views.download, name='download'),
]

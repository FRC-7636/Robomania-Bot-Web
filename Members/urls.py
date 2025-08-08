# coding=utf-8
from django.urls import path
from . import views

urlpatterns = [
    path("info/<int:member_id>", views.info),
]

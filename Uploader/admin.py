# coding=utf-8
from django.contrib import admin

from .models import UserFile, MDImage


# Register your models here.
@admin.register(UserFile)
class UserFileAdmin(admin.ModelAdmin):
    list_display = ("uuid", "name", "mimetype", "uploader", "uploaded_at", "require_login", "require_password")
    search_fields = ("uuid", "name", "mimetype")
    list_filter = ("uploader", "require_login", "require_password")


@admin.register(MDImage)
class MDImageAdmin(admin.ModelAdmin):
    list_display = ("uuid", "uploader", "uploaded_at")
    search_fields = ("uuid",)
    list_filter = ("uploader",)

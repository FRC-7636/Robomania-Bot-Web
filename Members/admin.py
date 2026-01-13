# coding=utf-8
from django.contrib import admin

from .models import DMember, WarningHistory


# Register your models here.
@admin.register(DMember)
class DMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "discord_id", "real_name", "gen", "warning_points", "email_address", "allow_login")
    ordering = ("id",)
    search_fields = ("discord_id", "real_name", "email_address")
    list_filter = ("gen", "allow_login")


@admin.register(WarningHistory)
class WarningHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "member", "points", "reason", "operator", "time")
    search_fields = ("reason",)
    list_filter = ("member", "operator", "reason")

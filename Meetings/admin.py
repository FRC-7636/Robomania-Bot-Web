# coding=utf-8
from django.contrib import admin
from .models import DMeeting, DAbsentRequest, MeetingSignIn, SingInRecord


# Register your models here.
@admin.register(DMeeting)
class DMeetingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "host",
        "start_time",
        "end_time",
        "can_absent",
        "location",
    )
    list_display_links = ("id", "name")
    search_fields = ("name", "host__discord_id", "host__real_name", "location")
    list_filter = ("host", "can_absent", "location")


@admin.register(DAbsentRequest)
class DAbsentRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "member",
        "meeting",
        "created_at",
        "status_display",
        "reviewer",
    )
    list_display_links = ("id", "member")
    search_fields = (
        "meeting__name",
        "reason",
        "reviewer__discord_id",
        "reviewer__real_name",
    )
    list_filter = ("member", "meeting", "status", "reviewer")

    @admin.display(description="審核狀態", boolean=True)
    def status_display(self, absent_request: DAbsentRequest):
        if absent_request.status == "approved":
            return True
        if absent_request.status == "rejected":
            return False
        return None


@admin.register(MeetingSignIn)
class MeetingSignInAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "meeting", "creator", "started_at", "ended_at")
    list_display_links = ("id", "uuid")
    search_fields = (
        "uuid",
        "meeting__name",
    )
    list_filter = ("meeting", "creator")


@admin.register(SingInRecord)
class SingInRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sign_in_method__meeting",
        "member",
        "signed_in_at",
        "sign_in_method__uuid",
    )
    search_fields = ("sign_in_method__uuid", "sign_in_method__meeting__name")
    list_filter = ("member", "sign_in_method__meeting", "sign_in_method")

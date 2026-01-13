# coding=utf-8
from django.contrib import admin
from django.utils import timezone

from datetime import timedelta

from .models import LoginCode


# Register your models here.
@admin.register(LoginCode)
class LoginCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "member",
        "created_at",
    )
    list_display_links = ("code",)
    list_filter = ("member",)
    actions = ("delete_expired_codes",)

    @admin.action(description="刪除過期的登入代碼")
    def delete_expired_codes(self, request, queryset):
        expiration_time = timezone.now() - timedelta(seconds=90)
        expired_codes = queryset.filter(created_at__lt=expiration_time)
        count = expired_codes.count()
        expired_codes.delete()
        self.message_user(request, f"已刪除 {count} 個過期的登入代碼。", "SUCCESS")

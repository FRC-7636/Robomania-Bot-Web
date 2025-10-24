# coding=utf-8
from django.db import models
from django.forms import ModelForm

from uuid import uuid4
import datetime


def everyone_mention():
    return ['@everyone']


# Create your models here.
class DMeeting(models.Model):
    class Meta:
        verbose_name = "會議"
        verbose_name_plural = "會議"

    def __str__(self):
        return f"{self.name} (#{self.pk})"

    name = models.CharField("名稱", max_length=255)
    creator = models.ForeignKey(
        "Members.DMember",
        verbose_name="創建者",
        related_name="created_meetings",
        on_delete=models.SET_NULL,
        null=True,
    )
    host = models.ForeignKey(
        "Members.DMember",
        verbose_name="主持人",
        related_name="hosted_meetings",
        on_delete=models.SET_NULL,
        null=True,
    )
    start_time = models.DateTimeField("開始時間")
    end_time = models.DateTimeField("結束時間", blank=True, null=True)
    can_absent = models.BooleanField("允許請假", default=True)
    description = models.TextField("說明", blank=True, null=True)
    location = models.CharField("地點")
    discord_mentions = models.JSONField(
        "Discord 通知提及", default=everyone_mention, blank=True
    )
    discord_notify_time = models.DurationField(
        "Discord 提前通知時間", default=datetime.timedelta(minutes=5), blank=True
    )


class DMeetingForm(ModelForm):
    class Meta:
        model = DMeeting
        fields = [
            "name",
            "start_time",
            "end_time",
            "can_absent",
            "description",
            "location",
            "discord_mentions",
        ]


class DAbsentRequest(models.Model):
    class Meta:
        verbose_name = "假單"
        verbose_name_plural = "假單"

    def __str__(self):
        return f"{self.meeting} - {self.member}"

    member = models.ForeignKey(
        "Members.DMember", verbose_name="成員", on_delete=models.CASCADE
    )
    meeting = models.ForeignKey(
        DMeeting,
        verbose_name="會議",
        related_name="absent_requests",
        on_delete=models.CASCADE,
    )
    reason = models.TextField("請假事由")
    status = models.CharField(
        "狀態",
        max_length=20,
        choices=[("pending", "待審核"), ("approved", "已批准"), ("rejected", "已拒絕")],
        default="pending",
    )
    created_at = models.DateTimeField("創建時間", auto_now_add=True)
    reviewer = models.ForeignKey(
        "Members.DMember",
        verbose_name="審核人",
        related_name="reviewed_requests",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )
    reviewer_comment = models.TextField("審核意見", blank=True, null=True)


class MeetingSignIn(models.Model):
    class Meta:
        verbose_name = "會議簽到"
        verbose_name_plural = "會議簽到"

    def __str__(self):
        return f"{self.uuid} - {self.meeting}"

    creator = models.ForeignKey(
        "Members.DMember",
        verbose_name="創建者",
        related_name="created_sign_ins",
        on_delete=models.SET_NULL,
        null=True,
    )
    meeting = models.ForeignKey(
        DMeeting, verbose_name="會議", related_name="sign_ins", on_delete=models.CASCADE
    )
    uuid = models.UUIDField("ID", unique=True, default=uuid4)
    started_at = models.DateTimeField("開放時間")
    ended_at = models.DateTimeField("關閉時間", blank=True, null=True)


class SingInRecord(models.Model):
    class Meta:
        verbose_name = "簽到記錄"
        verbose_name_plural = "簽到記錄"

    def __str__(self):
        return f"{self.member} - {self.sign_in_method.uuid}"

    member = models.ForeignKey(
        "Members.DMember", verbose_name="成員", on_delete=models.CASCADE
    )
    sign_in_method = models.ForeignKey(
        MeetingSignIn,
        verbose_name="簽到中介",
        related_name="records",
        on_delete=models.CASCADE,
        default=None,
    )
    signed_in_at = models.DateTimeField("簽到時間", auto_now_add=True)

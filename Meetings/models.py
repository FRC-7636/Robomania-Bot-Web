# coding=utf-8
from django.db import models


# Create your models here.
class DMeeting(models.Model):
    class Meta:
        verbose_name = "會議"
        verbose_name_plural = "會議"

    def __str__(self):
        return self.name

    name = models.CharField("名稱", max_length=255)
    creator = models.ForeignKey('Members.DMember', verbose_name="創建者", related_name="created_meetings",
                                on_delete=models.SET_NULL, null=True)
    host = models.ForeignKey('Members.DMember', verbose_name="主持人", related_name="hosted_meetings",
                             on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField("開始時間")
    end_time = models.DateTimeField("結束時間", blank=True, null=True)
    can_absent = models.BooleanField("允許請假", default=True)
    description = models.TextField("說明", blank=True, null=True)
    location = models.CharField("地點")
    participants = models.ManyToManyField('Members.DMember', verbose_name="參與者", related_name="meetings", blank=True)


class DAbsentRequest(models.Model):
    class Meta:
        verbose_name = "假單"
        verbose_name_plural = "假單"

    def __str__(self):
        return f"{self.member} - {self.meeting}"

    member = models.ForeignKey('Members.DMember', verbose_name="成員", on_delete=models.CASCADE)
    meeting = models.ForeignKey(DMeeting, verbose_name="會議", related_name="absent_requests", on_delete=models.CASCADE)
    reason = models.TextField("請假事由")
    status = models.CharField("狀態", max_length=20,
                              choices=[('pending', '待審核'), ('approved', '已批准'), ('rejected', '已拒絕')],
                              default='pending')
    created_at = models.DateTimeField("創建時間", auto_now_add=True)

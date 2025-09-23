# coding=utf-8
from django.db import models


# Create your models here.
class Announcement(models.Model):
    class Meta:
        verbose_name = "公告"
        verbose_name_plural = "公告"

    def __str__(self):
        return f"{self.title} (#{self.pk})"

    title = models.CharField("標題", max_length=255)
    content = models.TextField("內容")
    author = models.ForeignKey('Members.DMember', verbose_name="作者", related_name="created_announcements",
                               on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField("創建時間", auto_now_add=True)
    updated_at = models.DateTimeField("更新時間", auto_now=True)
    is_published = models.BooleanField("已發布", default=False)
    sync_to_discord = models.BooleanField("同步發布至 Discord", default=False)
    published_at = models.DateTimeField("發布時間", blank=True, null=True)
    is_pinned = models.BooleanField("置頂", default=False)
    pin_until = models.DateTimeField("置頂期限", blank=True, null=True)

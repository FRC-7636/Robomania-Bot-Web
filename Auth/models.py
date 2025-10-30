# coding=utf-8
from django.db import models

from Members.models import DMember


def generate_login_code():
    import string
    import random

    length = 8
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


class LoginCode(models.Model):
    class Meta:
        verbose_name = "登入代碼"
        verbose_name_plural = "登入代碼"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} for {self.member}"

    member = models.ForeignKey(DMember, verbose_name="成員", related_name="login_codes", on_delete=models.CASCADE)
    code = models.CharField("代碼", max_length=20, default=generate_login_code, unique=True)
    created_at = models.DateTimeField("建立時間", auto_now_add=True)

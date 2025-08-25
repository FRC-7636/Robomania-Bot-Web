# coding=utf-8
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager


# Create your models here.
class DMemberManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, discord_id, password, **extra_fields):
        if not discord_id:
            raise ValueError("Discord ID must be set")
        if not password:
            raise ValueError("Password must be set")
        user = self.model(discord_id=discord_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, discord_id, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(discord_id, password, **extra_fields)


def user_avatar_path(instance, filename):
    """
    Generate a path for user avatars based on their Discord ID.
    """
    return f"avatars/{instance.discord_id}/{filename}"


class DMember(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = "成員"
        verbose_name_plural = "成員"

    def __str__(self):
        return f"{self.discord_id} ({self.real_name})"

    username = None
    discord_id = models.PositiveBigIntegerField("Discord ID", unique=True)
    real_name = models.CharField("真實姓名", blank=True, null=True)
    gen = models.PositiveIntegerField("屆別", blank=True, null=True)
    jobs = models.JSONField("職務", blank=True, null=True)
    warning_points = models.FloatField("警告點數", default=0.0)
    email_address = models.EmailField("Email", blank=True, null=True)
    avatar = models.URLField("頭像", blank=True, null=True)

    is_staff = models.BooleanField(default=False)
    objects = DMemberManager()

    USERNAME_FIELD = "discord_id"
    EMAIL_FIELD = "email_address"
    REQUIRED_FIELDS = ["real_name"]


class WarningHistory(models.Model):
    class Meta:
        verbose_name = "記點歷史"
        verbose_name_plural = "記點歷史"
        ordering = ["-time"]

    def __str__(self):
        return f"{self.member} - {self.points} ({self.reason})"

    member = models.ForeignKey(DMember, verbose_name="成員", related_name="warning_history", on_delete=models.CASCADE)
    operator = models.ForeignKey(
        DMember, verbose_name="操作人員", related_name="operated_warnings", on_delete=models.CASCADE,
    )
    time = models.DateTimeField("時間", auto_now_add=True)
    reason = models.TextField("事由")
    points = models.FloatField("點數", default=0.0)
    notes = models.TextField("附註", blank=True, null=True)

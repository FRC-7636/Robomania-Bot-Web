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
    member = models.ForeignKey(DMember, on_delete=models.CASCADE)
    time = models.DateTimeField()
    reason = models.TextField()
    points = models.FloatField(default=0.0)
    notes = models.TextField(blank=True, null=True)

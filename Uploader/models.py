# coding=utf-8
from django.db import models
from django.forms import ModelForm
from django.contrib.auth.hashers import make_password
from uuid import uuid4


def file_path(instance, filename):
    """
    Generate a file path for the uploaded file.
    The path will be 'uploader/<uuid>/<filename>'.
    """
    return f"uploader/{instance.uuid}"


# Create your models here.
class UserFile(models.Model):
    class Meta:
        verbose_name = "使用者檔案"
        verbose_name_plural = "使用者檔案"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.name} ({self.mimetype})"

    file = models.FileField("檔案物件", upload_to=file_path, max_length=300)
    uuid = models.UUIDField("UUID", default=uuid4, editable=False, unique=True)
    name = models.CharField("名稱", help_text="使用者下載檔案時，將顯示此名稱", max_length=20)
    mimetype = models.CharField("MIME 類型", max_length=255)
    uploader = models.ForeignKey("Members.DMember", verbose_name="上傳者", on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField("上傳時間", auto_now_add=True)
    require_login = models.BooleanField("需登入才可存取", default=False)


class UserFileForm(ModelForm):
    class Meta:
        model = UserFile
        fields = ['file', 'name']
        labels = {
            'file': '檔案物件',
            'name': '名稱',
        }

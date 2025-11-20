# coding=utf-8
from django.contrib import admin

from .models import UserFile, MDImage


# Register your models here.
admin.site.register(UserFile)
admin.site.register(MDImage)

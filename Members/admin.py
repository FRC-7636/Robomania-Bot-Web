# coding=utf-8
from django.contrib import admin
from .models import DMember, WarningHistory

# Register your models here.
admin.site.register(DMember)
admin.site.register(WarningHistory)

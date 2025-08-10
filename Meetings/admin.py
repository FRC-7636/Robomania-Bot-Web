# coding=utf-8
from django.contrib import admin
from .models import DMeeting, DAbsentRequest

# Register your models here.
admin.site.register(DMeeting)
admin.site.register(DAbsentRequest)

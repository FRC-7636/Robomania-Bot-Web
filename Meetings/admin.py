# coding=utf-8
from django.contrib import admin
from .models import DMeeting, DAbsentRequest, MeetingSignIn, SingInRecord

# Register your models here.
admin.site.register(DMeeting)
admin.site.register(DAbsentRequest)
admin.site.register(MeetingSignIn)
admin.site.register(SingInRecord)

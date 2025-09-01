# coding=utf-8
from rest_framework import serializers
from .models import DMeeting


class DMeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DMeeting
        fields = "__all__"

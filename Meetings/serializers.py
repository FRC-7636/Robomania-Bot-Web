# coding=utf-8
from rest_framework import serializers

from .models import DMeeting, DAbsentRequest


class DMeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DMeeting
        fields = "__all__"


class DAbsentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DAbsentRequest
        fields = "__all__"

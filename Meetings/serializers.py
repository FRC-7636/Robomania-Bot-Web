# coding=utf-8
from rest_framework import serializers

from .models import DMeeting, DAbsentRequest


class DMeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DMeeting
        fields = "__all__"

    def to_representation(self, instance: DMeeting):
        representation = super().to_representation(instance)
        representation["discord_notify_time"] = instance.discord_notify_time.total_seconds()
        return representation


class DAbsentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DAbsentRequest
        fields = "__all__"

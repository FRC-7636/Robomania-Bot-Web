# coding=utf-8
from rest_framework import serializers
from .models import DMember, WarningHistory


class DMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = DMember
        fields = [
            "discord_id",
            "real_name",
            "email_address",
            "gen",
            "jobs",
            "avatar",
            "warning_points",
        ]

    def to_representation(self, instance):
        pk = instance.pk
        representation = super().to_representation(instance)
        representation["id"] = pk
        return representation


class WarningHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WarningHistory
        fields = "__all__"

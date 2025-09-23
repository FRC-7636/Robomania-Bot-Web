# coding=utf-8
from rest_framework import serializers
from .models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = "__all__"

    def to_representation(self, instance):
        pk = instance.pk
        representation = super().to_representation(instance)
        representation["id"] = pk
        return representation

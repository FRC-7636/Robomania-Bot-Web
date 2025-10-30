# coding=utf-8
from rest_framework import serializers

from .models import LoginCode


class LoginCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginCode
        fields = "__all__"

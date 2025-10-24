# coding=utf-8
from django import template
from datetime import timedelta

register = template.Library()


@register.filter("to_dc_val")
def to_dc_val(channel_id):
    return f"dc-{channel_id}"

# coding=utf-8
from django import template
from datetime import timedelta

register = template.Library()


@register.filter("timedelta_minutes")
def timedelta_minutes(td):
    if not isinstance(td, timedelta):
        return 5
    return int(td.total_seconds() // 60)

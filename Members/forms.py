# coding=utf-8
from django import forms


class BulkEditForm(forms.Form):
    member_ids = forms.JSONField(required=True)
    gen = forms.IntegerField(min_value=1, max_value=10, required=False)
    reason = forms.CharField(max_length=20, required=False)
    points = forms.FloatField(min_value=-5.0, max_value=5.0, required=False)
    notes = forms.CharField(max_length=100, required=False)

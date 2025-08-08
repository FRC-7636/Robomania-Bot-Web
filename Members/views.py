# coding=utf-8
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from .models import DMember


# Create your views here.
@login_required
def info(request, member_id):
    member = get_object_or_404(DMember, discord_id=member_id)
    return render(
        request,
        'Members/info.html',
        {"member_info": member}
    )

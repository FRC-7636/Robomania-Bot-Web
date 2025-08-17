# coding=utf-8
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from .models import DMember


# Create your views here.
@login_required
def info(request, member_id):
    member = get_object_or_404(DMember, discord_id=member_id)
    data = {"member": member,
            "warning_history": member.warning_history.all(),
            "is_self": member.discord_id == request.user.discord_id,
            "can_edit": request.user.has_perm("Members.change_DMember") or member.discord_id == request.user.discord_id,
            "can_edit_warning_points": request.user.has_perms(["Members.change_DMember", "Members.add_WarningHistory"])}
    return render(
        request,
        'Members/index.html',
        data
    )

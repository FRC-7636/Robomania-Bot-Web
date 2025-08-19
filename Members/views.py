# coding=utf-8
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from json import loads, JSONDecodeError

from .models import DMember


def sort_groups(groups: list[str]) -> dict[str, list[str]]:
    dept_groups, identity_groups = [], []
    for group in groups:
        if group.startswith("(D)"):
            dept_groups.append(group)
        elif group.startswith("(I)"):
            identity_groups.append(group)
    dept_groups.sort()
    identity_groups.sort()
    return {
        "dept_groups": dept_groups,
        "identity_groups": identity_groups,
    }


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


@login_required
def edit(request, member_id):
    if request.user.has_perm("Members.change_DMember") or request.user.discord_id == member_id:
        member = get_object_or_404(DMember, discord_id=member_id)
        if request.method == "POST":
            member.real_name = request.POST["real_name"]
            member.email_address = request.POST["email_address"]
            if request.user.has_perm("Members.change_DMember"):
                try:
                    edited_groups = loads(request.POST["groups"])
                except JSONDecodeError as je:
                    return HttpResponseBadRequest(je.msg)
                if isinstance(edited_groups, list):
                    member.groups.clear()
                    for group_name in edited_groups:
                        group = get_object_or_404(Group, name=group_name)
                        member.groups.add(group)
                else:
                    return HttpResponseBadRequest("Invalid group data format.")
            member.save()
            return redirect("member_info", member_id=member_id)
        else:
            groups = sort_groups([group.name for group in Group.objects.all()])
            joined_groups = [group.name for group in member.groups.all()]
            data = {"member": member,
                    "all_groups": groups,
                    "joined_groups": joined_groups,
                    "can_edit_groups": request.user.has_perm("Members.change_DMember")}
            return render(
                request,
                'Members/edit.html',
                data
            )
    else:
        return HttpResponseForbidden()

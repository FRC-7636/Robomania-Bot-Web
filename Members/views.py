# coding=utf-8
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from json import load, loads, JSONDecodeError
from pprint import pprint
from os import path
from logging import warning

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import DMember, WarningHistory
from .serializers import DMemberSerializer, WarningHistorySerializer


TEAM_RULES = {"negative": [], "positive": []}


def reload_team_rules():
    global TEAM_RULES
    if path.exists("team_rules.json"):
        with open("team_rules.json", "r", encoding="utf-8") as f:
            TEAM_RULES = load(f)
    else:
        warning("No team rules file found")


reload_team_rules()


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
    data = {
        "member": member,
        "warning_history": member.warning_history.all(),
        "is_self": member.discord_id == request.user.discord_id,
        "can_edit": request.user.has_perm("Members.change_dmember"),
        "can_edit_warning_points": request.user.has_perms(
            ["Members.change_dmember", "Members.add_warninghistory"]
        ),
    }
    return render(request, "Members/index.html", data)


@login_required
def list_members(request):
    members = DMember.objects.all()
    if request.GET.get("order_by", "").replace("-", "") not in (
        "pk",
        "discord_id",
        "real_name",
        "gen",
        "warning_points",
        "email_address",
    ):
        return redirect(f"{reverse('member_list')}?order_by=pk")
    members = members.order_by(request.GET["order_by"])
    return render(request, "Members/list.html", {"members": members})


@login_required
@permission_required("Members.change_dmember")
def edit(request, member_id):
    member = get_object_or_404(DMember, discord_id=member_id)
    if request.method == "POST":
        member.real_name = request.POST["real_name"]
        member.email_address = request.POST["email_address"]
        if request.POST["gen"].isdigit() and 1 <= int(request.POST["gen"]) <= 10:
            member.gen = int(request.POST["gen"])
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
        data = {
            "member": member,
            "all_groups": groups,
            "joined_groups": joined_groups,
        }
        return render(request, "Members/edit.html", data)


@login_required
@permission_required(
    ["Members.change_dmember", "Members.add_warninghistory"], raise_exception=True
)
def edit_warning_points(request, member_id):
    member = get_object_or_404(DMember, discord_id=member_id)
    if request.method == "POST":
        if abs(float(request.POST["points"])) > 5:
            return HttpResponseBadRequest("單次增減點數不可超過 5 點。")
        warn_history = WarningHistory(
            member=member,
            operator=request.user,
            reason=request.POST["reason"],
            points=request.POST["points"],
            notes=request.POST["notes"],
        )
        warn_history.save()
        points_before = member.warning_points
        member.warning_points = points_before + float(request.POST["points"])
        member.save()
        if member.warning_points < 0:
            auto_warn_history = WarningHistory(
                member=member,
                operator=request.user,
                reason="自動補正",
                points=-member.warning_points,
                notes="為避免點數為負，系統自動補足點數至 0。",
            )
            auto_warn_history.save()
            member.warning_points = 0.0
            member.save()
        # send websocket notification after autocorrection
        channel = get_channel_layer()
        async_to_sync(channel.group_send)(
            "member_updates",
            {
                "type": "member.add_warning_points",
                "warning_detail": WarningHistorySerializer(warn_history).data,
            },
        )
        return redirect("member_info", member_id=member_id)
    else:
        reload_team_rules()
        data = {"member": member, "team_rules": TEAM_RULES}
        return render(request, "Members/edit_warning_points.html", data)


class MembersViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [DjangoModelPermissions]

    filterset_fields = ("discord_id", "real_name", "email_address", "gen", "warning_points")

    queryset = DMember.objects.all()
    serializer_class = DMemberSerializer

    @action(methods=["GET"], detail=False)
    def bad_guys(self, request):
        bad_guys = DMember.objects.filter(warning_points__gt=0).order_by("-warning_points")
        serializer = self.get_serializer(bad_guys, many=True)
        return Response(serializer.data)

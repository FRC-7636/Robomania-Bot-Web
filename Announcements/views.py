# coding=utf-8
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required, permission_required

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import logging
import datetime
from zoneinfo import ZoneInfo
from pprint import pprint
from os import getenv
import requests

from .models import Announcement
from .serializers import AnnouncementSerializer

TAIPEI_TZ = ZoneInfo("Asia/Taipei")


def validate_announcement_data(data) -> tuple[bool, str]:
    if not data.get("title"):
        return False, "title"
    if not data.get("content"):
        return False, "content"
    if data.get("is_pinned", "false").lower() == "true":
        if not data.get("pin_until"):
            return False, "pin_until"
        try:
            pin_until = datetime.datetime.fromisoformat(
                data.get("pin_until")
            ).astimezone(TAIPEI_TZ)
            if not pin_until > datetime.datetime.now(TAIPEI_TZ):
                return False, "pin_until"
        except Exception as e:
            pprint(e)
            return False, "pin_until"
    return True, ""


def announce_to_discord(announcement: Announcement):
    message = f"""\
@everyone
> 此公告由 Robomania Bot Web 同步發布至此。
> 發布時間：<t:{int(announcement.published_at.timestamp())}:F>
> [點此查看公告詳情](https://frc7636.dpdns.org/announcement/{announcement.pk}/)
# {announcement.title}
{announcement.content}
"""
    if len(message) > 2000:
        message = message[:1997] + "..."
    webhook_url = getenv("DISCORD_WEBHOOK_URL")
    try:
        result = requests.post(
            webhook_url,
            headers={"Content-Type": "application/json"},
            json={
                "avatar_url": "https://frc7636.dpdns.org/static/img/7636.webp",
                "content": message
            },
        )
        if not result.ok:
            raise Exception(f"HTTP {result.status_code} ({result.text})")
        logging.info(f"Announcement #{announcement.pk} sent to Discord webhook.")
    except Exception as e:
        logging.error(
            f"Failed to send announcement #{announcement.pk} to Discord webhook: {e}"
        )
        # send websocket notification
        channel = get_channel_layer()
        async_to_sync(channel.group_send)(
            "announcement_updates",
            {
                "type": "announcement.announce",
                "announcement": AnnouncementSerializer(announcement).data,
            },
        )
        logging.info(f"Announcement #{announcement.pk} sent via websocket as fallback.")


# Create your views here.
@login_required
def index(request, announcement_id: int):
    announcement = get_object_or_404(Announcement, pk=announcement_id)
    announcement_content = announcement.content.replace("`", "\\`")
    return render(
        request,
        "Announcements/index.html",
        {
            "announcement": announcement,
            "announcement_content": announcement_content,
            "can_edit": request.user.has_perm("Announcements.change_Announcement"),
        },
    )


@login_required
@permission_required("Announcements.add_announcement", raise_exception=True)
def create_view(request):
    if request.method == "POST":
        is_valid, error_field = validate_announcement_data(request.POST)
        if not is_valid:
            return HttpResponseBadRequest(f"Invalid data: {error_field}")
        title = request.POST.get("title", None)
        content = request.POST.get("content", None)
        is_pinned = request.POST.get("is_pinned", "false").lower() == "true"
        if is_pinned:
            pin_due_date = datetime.datetime.fromisoformat(
                request.POST.get("pin_until", None)
            ).astimezone(TAIPEI_TZ)
        else:
            pin_due_date = None
        announcement = Announcement(
            title=title,
            content=content,
            updated_at=datetime.datetime.now(TAIPEI_TZ),
            author=request.user,
            is_pinned=is_pinned,
            pin_until=pin_due_date,
        )
        submit_type = request.POST.get("submit-type", "save")
        if "announce" in submit_type:
            announcement.is_published = True
            announcement.published_at = datetime.datetime.now(TAIPEI_TZ)
            if submit_type == "announce-with-dc":
                announce_to_discord(announcement)
                announcement.sync_to_discord = True
        announcement.save()
        if is_pinned:
            # send websocket notification
            channel = get_channel_layer()
            async_to_sync(channel.group_send)(
                "announcement_updates",
                {
                    "type": "announcement.pin",
                    "announcement": AnnouncementSerializer(announcement).data,
                },
            )
        return redirect("announcement_info", announcement_id=announcement.pk)
    else:
        return render(request, "Announcements/edit.html", {})


@login_required
@permission_required(
    ["Announcements.change_announcement", "Announcements.delete_announcement"],
    raise_exception=True,
)
def edit_view(request, announcement_id: int):
    if request.method == "POST":
        is_valid, error_field = validate_announcement_data(request.POST)
        if not is_valid:
            return HttpResponseBadRequest(f"Invalid data: {error_field}")
        title = request.POST.get("title", None)
        content = request.POST.get("content", None)
        is_pinned = request.POST.get("is_pinned", "false").lower() == "true"
        if is_pinned:
            pin_due_date = datetime.datetime.fromisoformat(
                request.POST.get("pin_until", None)
            ).astimezone(TAIPEI_TZ)
        else:
            pin_due_date = None
        announcement = get_object_or_404(Announcement, pk=announcement_id)
        announcement.title = title
        announcement.content = content
        announcement.updated_at = datetime.datetime.now(TAIPEI_TZ)
        if is_pinned:
            announcement.is_pinned = True
            announcement.pin_until = pin_due_date
            # send websocket notification
            channel = get_channel_layer()
            async_to_sync(channel.group_send)(
                "announcement_updates",
                {
                    "type": "announcement.pin",
                    "announcement": AnnouncementSerializer(announcement).data,
                },
            )
        else:
            if announcement.is_pinned:
                # send websocket notification only if the announcement was pinned before
                channel = get_channel_layer()
                async_to_sync(channel.group_send)(
                    "announcement_updates",
                    {
                        "type": "announcement.unpin",
                        "announcement_id": announcement.id,
                    },
                )
            announcement.is_pinned = False
            announcement.pin_until = None
        submit_type = request.POST.get("submit-type", "save")
        if "announce" in submit_type and not announcement.is_published:
            announcement.is_published = True
            announcement.published_at = datetime.datetime.now(TAIPEI_TZ)
        if submit_type == "announce-with-dc" and not announcement.sync_to_discord:
            announce_to_discord(announcement)
            announcement.sync_to_discord = True
        announcement.save()
        return redirect("announcement_info", announcement_id=announcement.pk)
    else:
        announcement = get_object_or_404(Announcement, pk=announcement_id)
        announcement_content = announcement.content.replace("`", "\\`")
        return render(
            request,
            "Announcements/edit.html",
            {
                "announcement": announcement,
                "announcement_content": announcement_content,
                "published": announcement.is_published,
                "synced_to_dc": announcement.sync_to_discord,
            },
        )


@login_required
@permission_required(
    ["Announcements.change_announcement", "Announcements.delete_announcement"],
    raise_exception=True,
)
def delete_view(request, announcement_id: int):
    announcement = get_object_or_404(Announcement, pk=announcement_id)
    if request.method == "DELETE":
        announcement_data = AnnouncementSerializer(announcement).data
        announcement.delete()
        channel = get_channel_layer()
        async_to_sync(channel.group_send)(
            "announcement_updates",
            {
                "type": "announcement.delete",
                "announcement": announcement_data,
            },
        )
        return HttpResponse(status=204)
    else:
        return HttpResponse("Method not allowed", status=405)


@login_required
def list_view(request):
    if request.GET.get("order_by", "").replace("-", "") not in (
        "pk",
        "created_at",
        "published_at",
        "pin_until",
    ):
        return redirect(f"{reverse('announcement_list')}?order_by=pk")
    if request.user.has_perm("Announcements.change_announcement"):
        pinned_announcements = Announcement.objects.filter(is_pinned=True)
        other_announcements = Announcement.objects.filter(is_pinned=False)
    else:
        pinned_announcements = Announcement.objects.filter(
            is_pinned=True, is_published=True
        )
        other_announcements = Announcement.objects.filter(
            is_pinned=False, is_published=True
        )
    return render(
        request,
        "Announcements/list.html",
        {
            "can_create": request.user.has_perm("Announcements.add_announcement"),
            "pinned_announcements": pinned_announcements.order_by(
                request.GET["order_by"]
            ),
            "other_announcements": other_announcements.order_by(
                request.GET["order_by"]
            ),
        },
    )


class AnnouncementsViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [DjangoModelPermissions]

    filterset_fields = [
        "author__discord_id",
        "created_at",
        "is_published",
        "published_at",
        "sync_to_discord",
        "is_pinned",
        "pin_until",
    ]

    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

    @action(["GET"], detail=False)
    def pinned(self, request):
        pinned_announcements = Announcement.objects.filter(is_pinned=True)
        serializer = self.get_serializer(pinned_announcements, many=True)
        return Response(serializer.data)

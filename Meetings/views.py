# coding=utf-8
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
import datetime
from zoneinfo import ZoneInfo
from json import loads

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import DMeeting, DAbsentRequest
from .serializers import DMeetingSerializer, DAbsentRequestSerializer
from Members.models import DMember

TAIPEI_TZ = ZoneInfo("Asia/Taipei")


def validate_meeting_data(data):
    if not data.get("name"):
        return False, "name"
    if not data.get("host"):
        return False, "host"
    else:
        host_id = int(data["host"])
        if not DMember.objects.filter(discord_id=host_id).exists():
            return False, "host"
    if not data.get("start-time"):
        return False, "start-time (missing)"
    try:
        start_time = datetime.datetime.fromisoformat(data["start-time"]).astimezone(
            TAIPEI_TZ
        )
    except ValueError:
        return False, "start-time (incorrect format)"
    if data.get("end-time"):
        try:
            end_time = datetime.datetime.fromisoformat(data["end-time"]).astimezone(
                TAIPEI_TZ
            )
        except ValueError:
            return False, "end-time"
        if end_time < start_time:
            return False, "end-time"
    if not data.get("location"):
        return False, "location"
    if not data.get("can-absent"):
        return False, "can-absent"
    return True, ""


def update_upcoming_meetings():
    now = datetime.datetime.now(tz=TAIPEI_TZ)
    upcoming_meetings = DMeeting.objects.filter(start_time__gt=now).order_by(
        "start_time"
    )
    return upcoming_meetings


# Create your views here.
@login_required
def index(request, meeting_id):
    meeting = get_object_or_404(DMeeting, pk=meeting_id)
    now = datetime.datetime.now(tz=TAIPEI_TZ)
    reason_not_absent = ""
    if not meeting.can_absent:
        reason_not_absent = "此會議不允許請假。"
    elif meeting.start_time < now:
        reason_not_absent = "會議已經開始，無法請假。"
    elif (meeting.start_time - now) < datetime.timedelta(minutes=5):
        reason_not_absent = "請假最晚需在會議開始前 5 分鐘處理完畢。"
    elif meeting.absent_requests.filter(member=request.user).exists():
        reason_not_absent = "你已經提交了假單，無法再次提交。"
    condensed_absent_request = None
    if meeting.absent_requests.filter(member=request.user).exists():
        absent_request = meeting.absent_requests.get(member=request.user)
        condensed_absent_request = {
            "status": absent_request.status,
            "reason": absent_request.reason,
            "created_at": absent_request.created_at.astimezone(TAIPEI_TZ).strftime(
                "%Y/%m/%d %H:%M"
            ),
            "reviewer": absent_request.reviewer,
            "reviewer_comment": absent_request.reviewer_comment,
        }
    return render(
        request,
        "Meetings/index.html",
        {
            "meeting": meeting,
            "meeting_description": (
                meeting.description.replace("`", "\\`")
                if meeting.description is not None
                else ""
            ),
            "absent_request": condensed_absent_request,
            "can_send_absent_request": reason_not_absent == "",
            "reason_not_absent": reason_not_absent,
            "can_edit": (
                request.user.has_perm("Meetings.change_dmeeting")
                and request.user.has_perm("Meetings.delete_dmeeting")
            ),
        },
    )


@login_required
def list_view(request):
    meetings = DMeeting.objects.all()
    if request.GET.get("order_by", "").replace("-", "") not in (
        "pk",
        "name",
        "host",
        "start_time",
        "end_time",
        "can_absent",
    ):
        return redirect(f"{reverse('meeting_list')}?order_by=pk")
    meetings = meetings.order_by(request.GET["order_by"])
    return render(
        request,
        "Meetings/list.html",
        {
            "meetings": meetings,
            "can_create": request.user.has_perm("Meetings.add_dmeeting"),
        },
    )


@login_required
@permission_required("Meetings.add_dmeeting", raise_exception=True)
def create(request):
    if request.method == "POST":
        # validate form data
        is_valid, error_field = validate_meeting_data(request.POST)
        if not is_valid:
            return HttpResponse(f"Invalid data for field: {error_field}", status=400)
        # create new meeting
        meeting = DMeeting(
            name=request.POST.get("name", ""),
            description=request.POST.get("description", ""),
            host=DMember.objects.get(discord_id=int(request.POST.get("host", ""))),
            start_time=datetime.datetime.fromisoformat(
                request.POST.get("start-time")
            ).astimezone(TAIPEI_TZ),
            end_time=(
                datetime.datetime.fromisoformat(
                    request.POST.get("end-time")
                ).astimezone(TAIPEI_TZ)
                if request.POST.get("end-time", None)
                else None
            ),
            location=request.POST.get("location", ""),
            can_absent=request.POST.get("can-absent", "False").lower() == "true",
            creator=request.user,
        )
        # save meeting
        meeting.save()
        # send websocket notification
        channel = get_channel_layer()
        async_to_sync(channel.group_send)(
            "meeting_updates",
            {"type": "meeting.create", "meeting": DMeetingSerializer(meeting).data},
        )
        # redirect to meeting info page
        return redirect("meeting_info", meeting_id=meeting.pk)
    else:  # GET
        # generate member choices for host selector
        all_members = DMember.objects.all()
        member_choices = []
        for member in all_members:
            member_choices.append(
                {
                    "discord_id": member.discord_id,
                    "real_name": member.real_name,
                    "avatar": member.avatar,
                }
            )
        return render(request, "Meetings/edit.html", {"member_list": member_choices})


@login_required
@permission_required(
    ["Meetings.change_dmeeting", "Meetings.delete_dmeeting"], raise_exception=True
)
def edit(request, meeting_id):
    meeting = get_object_or_404(DMeeting, pk=meeting_id)
    if request.method == "POST":
        # update meeting
        is_valid, error_field = validate_meeting_data(request.POST)
        if not is_valid:
            return HttpResponse(f"Invalid data for field: {error_field}", status=400)
        meeting.name = request.POST.get("name", "")
        meeting.description = request.POST.get("description", "")
        meeting.host = DMember.objects.get(discord_id=int(request.POST.get("host", "")))
        meeting.start_time = datetime.datetime.fromisoformat(
            request.POST.get("start-time")
        ).astimezone(TAIPEI_TZ)
        if request.POST.get("end-time", None):
            meeting.end_time = datetime.datetime.fromisoformat(
                request.POST.get("end-time")
            ).astimezone(TAIPEI_TZ)
        else:
            meeting.end_time = None
        meeting.location = request.POST.get("location", "")
        meeting.can_absent = request.POST.get("can-absent", "False").lower() == "true"
        # save changes
        meeting.save()
        # send websocket notification
        channel = get_channel_layer()
        async_to_sync(channel.group_send)(
            "meeting_updates",
            {"type": "meeting.edit", "meeting": DMeetingSerializer(meeting).data},
        )
        return redirect("meeting_info", meeting_id=meeting_id)
    else:  # GET
        # generate member choices for host selector
        all_members = DMember.objects.all()
        member_choices = []
        for member in all_members:
            member_choices.append(
                {
                    "discord_id": member.discord_id,
                    "real_name": member.real_name,
                    "avatar": member.avatar,
                }
            )
        return render(
            request,
            "Meetings/edit.html",
            {
                "meeting": meeting,
                "meeting_description": (
                    meeting.description.replace("`", "\\`")
                    if meeting.description is not None
                    else ""
                ),
                "member_list": member_choices,
            },
        )


@login_required
@permission_required(
    ["Meetings.change_dmeeting", "Meetings.delete_dmeeting"], raise_exception=True
)
def delete(request, meeting_id):
    meeting = get_object_or_404(DMeeting, pk=meeting_id)
    if request.method == "DELETE":
        # save meeting data before deletion to save pk
        meeting_data = DMeetingSerializer(meeting).data
        # delete meeting
        meeting.delete()
        # send websocket notification
        channel = get_channel_layer()
        async_to_sync(channel.group_send)(
            "meeting_updates",
            {"type": "meeting.delete", "meeting": meeting_data},
        )
        return HttpResponse(status=204)
    else:
        return HttpResponse("Method not allowed", status=405)


@login_required
def submit_absent_request(request, meeting_id):
    meeting = get_object_or_404(DMeeting, pk=meeting_id)
    now = datetime.datetime.now(tz=TAIPEI_TZ)
    if not meeting.can_absent:
        return HttpResponse("You must attend this meeting.", status=403)
    elif meeting.start_time < now:
        return HttpResponse("The meeting has started.", status=403)
    elif (meeting.start_time - now) < datetime.timedelta(minutes=5):
        return HttpResponse(
            "Absent requests must be submitted at least 5 minutes before the meeting.",
            status=403,
        )
    elif meeting.absent_requests.filter(member=request.user).exists():
        return HttpResponse(
            "You have already submitted an absent request for this meeting.", status=403
        )
    if request.method == "POST":
        reason = request.POST.get("reason", None)
        if reason is None:
            return HttpResponse("Reason for absence is required.", status=400)
        absent_request = DAbsentRequest(
            member=request.user, meeting=meeting, reason=reason
        )
        absent_request.save()
        # send websocket notification
        channel = get_channel_layer()
        async_to_sync(channel.group_send)(
            "meeting_updates",
            {"type": "meeting.new_absent_request",
             "absent_request": DAbsentRequestSerializer(absent_request).data},
        )
        return redirect("meeting_info", meeting_id=meeting_id)
    else:
        return render(
            request, "Meetings/submit_absent_request.html", {"meeting": meeting}
        )


@login_required
@permission_required("Meetings.change_dabsentrequest", raise_exception=True)
def review_absent_requests_page(request, meeting_id):
    meeting = get_object_or_404(DMeeting, pk=meeting_id)
    absent_requests = meeting.absent_requests.all()
    pending_requests = absent_requests.filter(status="pending")
    reviewed_requests = absent_requests.exclude(status="pending")
    return render(
        request,
        "Meetings/review_absent_requests.html",
        {
            "meeting": meeting,
            "pending_requests": pending_requests,
            "reviewed_requests": reviewed_requests,
        },
    )


@login_required
@permission_required("Meetings.change_dabsentrequest", raise_exception=True)
def review_absent_requests_api(request, meeting_id):
    meeting = get_object_or_404(DMeeting, pk=meeting_id)
    if request.method == "POST":
        edit_requests = loads(request.POST.get("edited_requests", "{}"))
        for request_id, review_result in edit_requests.items():
            absent_request = meeting.absent_requests.get(pk=int(request_id))
            absent_request.reviewer = request.user
            absent_request.status = review_result["status"]
            absent_request.reviewer_comment = review_result["comment"]
            absent_request.save()
            # send websocket notification
            channel = get_channel_layer()
            async_to_sync(channel.group_send)(
                "meeting_updates",
                {"type": "meeting.review_absent_request",
                 "absent_request": DAbsentRequestSerializer(absent_request).data},
            )
        return HttpResponse(status=200)
    return HttpResponse("Method not allowed", status=405)


def test_ws(request):
    channel = get_channel_layer()
    async_to_sync(channel.group_send)(
        "meeting_updates", {"type": "test.message", "text": "This is a test message."}
    )
    return HttpResponse("Done", status=200)


class MeetingsViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [DjangoModelPermissions]

    filterset_fields = ['host__discord_id', 'start_time', 'end_time', 'can_absent']

    queryset = DMeeting.objects.all()
    serializer_class = DMeetingSerializer

    @action(methods=["GET"], detail=False)
    def upcoming(self, request):
        upcoming_meetings = update_upcoming_meetings()
        serializer = self.get_serializer(upcoming_meetings, many=True)
        return Response(serializer.data)


class AbsentRequestsViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [DjangoModelPermissions]

    filterset_fields = ['member__discord_id', 'meeting__id', 'status', 'created_at', 'reviewer__discord_id']

    queryset = DAbsentRequest.objects.all()
    serializer_class = DAbsentRequestSerializer

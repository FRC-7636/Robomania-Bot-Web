# coding=utf-8
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, reverse, get_object_or_404

import datetime
from zoneinfo import ZoneInfo
from json import loads, dumps

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import DMeeting, DMeetingForm, DAbsentRequest, MeetingSignIn, SingInRecord
from .serializers import DMeetingSerializer, DAbsentRequestSerializer
from .consumers import role_update_signal, channel_update_signal
from Members.models import DMember

TAIPEI_TZ = ZoneInfo("Asia/Taipei")
ROLES = []
CHANNELS = {}


def update_roles(**kwargs):
    global ROLES
    ROLES = kwargs.get("roles", [])


def update_channels(**kwargs):
    global CHANNELS
    CHANNELS = kwargs.get("channels", {})


role_update_signal.connect(update_roles)
channel_update_signal.connect(update_channels)


# Deprecated, use ModelForm validation instead
# def validate_meeting_data(data):
#     if not data.get("name"):
#         return False, "name"
#     if not data.get("host"):
#         return False, "host"
#     else:
#         host_id = int(data["host"])
#         if not DMember.objects.filter(discord_id=host_id).exists():
#             return False, "host"
#     if not data.get("start-time"):
#         return False, "start-time (missing)"
#     try:
#         start_time = datetime.datetime.fromisoformat(data["start-time"]).astimezone(
#             TAIPEI_TZ
#         )
#         if start_time + datetime.timedelta(minutes=int(data.get("discord_notify_time", "5"))) < datetime.datetime.now(
#             tz=TAIPEI_TZ
#         ):
#             return False, "discord-notify-time"
#     except ValueError:
#         return False, "start-time (incorrect format)"
#     if data.get("end-time"):
#         try:
#             end_time = datetime.datetime.fromisoformat(data["end-time"]).astimezone(
#                 TAIPEI_TZ
#             )
#         except ValueError:
#             return False, "end-time"
#         if end_time < start_time:
#             return False, "end-time"
#     if not data.get("location"):
#         return False, "location"
#     if not data.get("can-absent"):
#         return False, "can-absent"
#     return True, ""


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
    can_edit = request.user.has_perm(
        "Meetings.change_dmeeting"
    ) and request.user.has_perm("Meetings.delete_dmeeting")
    reviewed_absent_requests = meeting.absent_requests.exclude(status="pending")
    can_sign_in = request.user.has_perm("Meetings.add_meetingsignin") and not (
        meeting.end_time and meeting.end_time < now
    )
    if can_sign_in:
        sign_ins = meeting.sign_ins.all()
        condensed_sign_ins = []
        for sign_in in sign_ins:
            condensed_sign_ins.append(
                {
                    "creator": {
                        "discord_id": sign_in.creator.discord_id,
                        "real_name": sign_in.creator.real_name,
                        "avatar": sign_in.creator.avatar,
                    },
                    "uuid": str(sign_in.uuid),
                    "started_at": sign_in.started_at.astimezone(TAIPEI_TZ).strftime(
                        "%Y/%m/%d %H:%M:%S"
                    ),
                    "ended_at": sign_in.ended_at.astimezone(TAIPEI_TZ).strftime(
                        "%Y/%m/%d %H:%M:%S"
                    ),
                }
            )
    else:
        condensed_sign_ins = None
    sign_in_records = SingInRecord.objects.filter(
        sign_in_method__meeting=meeting
    ).order_by("-signed_in_at")
    condensed_sign_in_records = []
    for record in sign_in_records:
        condensed_sign_in_records.append(
            {
                "member": {
                    "discord_id": record.member.discord_id,
                    "real_name": record.member.real_name,
                    "avatar": record.member.avatar,
                },
                "signed_in_at": record.signed_in_at.astimezone(TAIPEI_TZ).strftime(
                    "%Y/%m/%d %H:%M:%S"
                ),
                "sign_in_uuid": str(record.sign_in_method.uuid),
            }
        )
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
            "records": condensed_sign_in_records,
            "absent_request": condensed_absent_request,
            "can_send_absent_request": reason_not_absent == "",
            "reason_not_absent": reason_not_absent,
            "can_edit": can_edit,
            "reviewed_absent_requests": reviewed_absent_requests,
            "can_sign_in": can_sign_in,
            "sign_ins": condensed_sign_ins,
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
        # use ModelForm to create meeting
        meeting = DMeetingForm(request.POST)
        # save meeting if form is valid
        if meeting.is_valid():
            # convert ModelForm to Model before saving
            meeting = meeting.save(commit=False)
            meeting.host = DMember.objects.get(discord_id=request.POST.get("host", ""))
            meeting.creator = request.user
            meeting.discord_notify_time = datetime.timedelta(
                minutes=int(
                    request.POST.get("discord_notify_time", "5")
                    if request.POST.get("discord_notify_time", "5") != ""
                    else "5"
                )
            )
            meeting.save()
        else:
            return HttpResponse(f"Invalid form data: {meeting.errors}", status=400)
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
        # use ModelForm to update meeting
        meeting = DMeetingForm(request.POST, instance=meeting)
        # save meeting if form is valid
        if meeting.is_valid():
            meeting = meeting.save(commit=False)
            meeting.host = DMember.objects.get(discord_id=request.POST.get("host", ""))
            meeting.creator = request.user
            meeting.discord_notify_time = datetime.timedelta(
                minutes=int(
                    request.POST.get("discord_notify_time", "5")
                    if request.POST.get("discord_notify_time", "5") != ""
                    else "5"
                )
            )
            meeting.save()
        else:
            return HttpResponse(f"Invalid form data: {meeting.errors}", status=400)
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
def sign_in_view(request, meeting_id, sign_in_uuid):
    meeting = get_object_or_404(DMeeting, pk=meeting_id)
    sign_in = get_object_or_404(MeetingSignIn, uuid=sign_in_uuid)
    record = None
    error = None
    now = datetime.datetime.now(tz=TAIPEI_TZ)
    if SingInRecord.objects.filter(
        sign_in_method__meeting=meeting, member=request.user
    ).exists():
        error = "你已簽到過這場會議。"
    elif sign_in.started_at > now:
        error = "此簽到連結尚未開放。"
    elif sign_in.ended_at and sign_in.ended_at < now:
        error = "此簽到連結已失效。"
    else:
        record = SingInRecord(member=request.user, sign_in_method=sign_in)
        record.save()
        # send websocket notification
        channel = get_channel_layer()
        async_to_sync(channel.group_send)(
            f"meeting_signin_{sign_in_uuid}",
            {
                "type": "signin.new_record",
                "record": {
                    "member": {
                        "discord_id": record.member.discord_id,
                        "real_name": record.member.real_name,
                        "avatar": record.member.avatar,
                    },
                    "signed_in_at": record.signed_in_at.astimezone(TAIPEI_TZ).strftime(
                        "%Y/%m/%d %H:%M:%S"
                    ),
                },
            },
        )
    return render(
        request,
        "Meetings/sign_in_result.html",
        {"meeting": meeting, "record": record, "error": error},
    )


@login_required
@permission_required(["Meetings.add_meetingsignin", "Meetings.change_meetingsignin"])
def sign_in_create_view(request, meeting_id):
    meeting = get_object_or_404(DMeeting, pk=meeting_id)
    if meeting.end_time and meeting.end_time < datetime.datetime.now(tz=TAIPEI_TZ):
        return HttpResponse("This meeting has already ended.", status=403)
    if request.method == "POST":
        # create new sign-in session
        now = datetime.datetime.now(tz=TAIPEI_TZ)
        start_time = datetime.datetime.fromisoformat(
            request.POST.get("started_at")
        ).astimezone(TAIPEI_TZ)
        if start_time < now:
            return HttpResponseBadRequest("Start time cannot be in the past.")
        if meeting.end_time and start_time > meeting.end_time:
            return HttpResponseBadRequest(
                "Start time cannot be after meeting end time."
            )
        sign_in = MeetingSignIn(
            creator=request.user,
            meeting=meeting,
            started_at=datetime.datetime.fromisoformat(request.POST.get("started_at")),
            ended_at=(
                datetime.datetime.fromisoformat(request.POST.get("started_at"))
                + datetime.timedelta(
                    minutes=int(
                        request.POST.get("duration", "15")
                        if request.POST.get("duration", "15") != ""
                        else "15"
                    )
                )
            ),
        )
        sign_in.save()
        return redirect(
            "meeting_signin_scan", meeting_id=meeting_id, sign_in_uuid=sign_in.uuid
        )
    else:  # GET
        return render(request, "Meetings/sign_in_create.html", {"meeting": meeting})


@login_required
@permission_required(["Meetings.add_meetingsignin", "Meetings.change_meetingsignin"])
def sign_in_scan_view(request, meeting_id, sign_in_uuid):
    meeting = get_object_or_404(DMeeting, pk=meeting_id)
    sign_in = get_object_or_404(MeetingSignIn, uuid=sign_in_uuid)
    if sign_in.ended_at and sign_in.ended_at < datetime.datetime.now(tz=TAIPEI_TZ):
        return HttpResponse("This sign-in session has already ended.", status=403)
    signed_in_record_count = SingInRecord.objects.filter(sign_in_method=sign_in).count()
    signed_in_records = SingInRecord.objects.filter(sign_in_method=sign_in).order_by(
        "-signed_in_at"
    )
    return render(
        request,
        "Meetings/sign_in_scan.html",
        {
            "meeting": meeting,
            "sign_in": sign_in,
            "signed_in_count": signed_in_record_count,
            "records": signed_in_records,
        },
    )


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
            {
                "type": "meeting.new_absent_request",
                "absent_request": DAbsentRequestSerializer(absent_request).data,
            },
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
        review_conflicts = []
        for request_id, review_result in edit_requests.items():
            absent_request = meeting.absent_requests.get(pk=int(request_id))
            if absent_request.status == "pending":
                absent_request.reviewer = request.user
                absent_request.status = review_result["status"]
                absent_request.reviewer_comment = review_result["comment"]
                absent_request.save()
                # send websocket notification
                channel = get_channel_layer()
                async_to_sync(channel.group_send)(
                    "meeting_updates",
                    {
                        "type": "meeting.review_absent_request",
                        "absent_request": DAbsentRequestSerializer(absent_request).data,
                    },
                )
            else:
                review_conflicts.append(
                    (
                        absent_request.member.real_name,
                        absent_request.reviewer.real_name,
                        absent_request.get_status_display(),
                    )
                )
        return HttpResponse(dumps(review_conflicts), status=200)
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

    filterset_fields = ["host__discord_id", "start_time", "end_time", "can_absent"]

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

    filterset_fields = [
        "member__discord_id",
        "meeting__id",
        "status",
        "created_at",
        "reviewer__discord_id",
    ]

    queryset = DAbsentRequest.objects.all()
    serializer_class = DAbsentRequestSerializer

# coding=utf-8
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
import datetime
from zoneinfo import ZoneInfo

from .models import DMeeting, DAbsentRequest
from Members.models import DMember

TAIPEI_TZ = ZoneInfo("Asia/Taipei")


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
            "created_at": absent_request.created_at.astimezone(TAIPEI_TZ).strftime("%Y/%m/%d %H:%M"),
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
                request.user.has_perm("Meetings.change_DMeeting")
                and request.user.has_perm("Meetings.delete_DMeeting")
            ),
        },
    )


@login_required
@permission_required(["Meetings.change_DMeeting", "Meetings.delete_DMeeting"], raise_exception=True)
def edit(request, meeting_id):
    meeting = get_object_or_404(DMeeting, pk=meeting_id)
    if request.method == "POST":
        # update meeting
        meeting.title = request.POST.get("title", "")
        meeting.description = request.POST.get("description", "")
        meeting.host = DMember.objects.get(discord_id=int(request.POST.get("host", "")))
        meeting.start_time = datetime.datetime.fromisoformat(request.POST.get("start-time")).astimezone(TAIPEI_TZ)
        if request.POST.get("end-time", None):
            meeting.end_time = datetime.datetime.fromisoformat(request.POST.get("end-time")).astimezone(TAIPEI_TZ)
        else:
            meeting.end_time = None
        meeting.location = request.POST.get("location", "")
        meeting.can_absent = request.POST.get("can-absent", "False").lower() == "true"
        # save changes
        meeting.save()
        return redirect("meeting_info", meeting_id=meeting_id)
    else:  # GET
        # generate member choices for host selector
        all_members = DMember.objects.all()
        member_choices = []
        for member in all_members:
            member_choices.append(
                {"discord_id": member.discord_id, "real_name": member.real_name, "avatar": member.avatar}
            )
        return render(request, 'Meetings/edit.html',
                      {"meeting": meeting,
                       "meeting_description":
                           meeting.description.replace("`", "\\`") if meeting.description is not None else "",
                       "member_list": member_choices})


@permission_required(["Meetings.change_DMeeting", "Meetings.delete_DMeeting"], raise_exception=True)
def delete(request, meeting_id):
    meeting = get_object_or_404(DMeeting, pk=meeting_id)
    if request.method == "DELETE":
        # delete meeting
        meeting.delete()
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
        absent_request = DAbsentRequest(member=request.user, meeting=meeting, reason=reason)
        absent_request.save()
        return redirect("meeting_info", meeting_id=meeting_id)
    else:
        return render(request, "Meetings/submit_absent_request.html", {"meeting": meeting})

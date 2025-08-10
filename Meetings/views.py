# coding=utf-8
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404, redirect
import datetime
from zoneinfo import ZoneInfo

from .models import DMeeting
from Members.models import DMember


# Create your views here.
@login_required
def index(request, meeting_id):
    meeting = get_object_or_404(DMeeting, pk=meeting_id)
    return render(request, 'Meetings/index.html',
                  {"meeting": meeting,
                   "meeting_description": meeting.description.replace("`",
                                                                      "\\`") if meeting.description is not None else "",
                   "can_edit": request.user.has_perm("Meetings.change_DMeeting") and request.user.has_perm(
                       "Meetings.delete_DMeeting")
                   })


@permission_required(["Meetings.change_DMeeting", "Meetings.delete_DMeeting"], raise_exception=True)
def edit(request, meeting_id):
    meeting = get_object_or_404(DMeeting, pk=meeting_id)
    if request.method == "POST":
        taipei_tz = ZoneInfo("Asia/Taipei")
        # update meeting
        meeting.title = request.POST.get("title", "")
        meeting.description = request.POST.get("description", "")
        meeting.host = DMember.objects.get(discord_id=int(request.POST.get("host", "")))
        meeting.start_time = datetime.datetime.fromisoformat(request.POST.get("start-time")).astimezone(taipei_tz)
        if request.POST.get("end-time", None):
            meeting.end_time = datetime.datetime.fromisoformat(request.POST.get("end-time")).astimezone(taipei_tz)
        else:
            meeting.end_time = None
        meeting.location = request.POST.get("location", "")
        meeting.can_absent = request.POST.get("can-absent", "False").lower() == "true"
        # save changes
        meeting.save()
        return redirect("meeting_info", meeting_id=meeting_id)
    elif request.method == "DELETE":
        # delete meeting
        meeting.delete()
        return redirect("index")
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

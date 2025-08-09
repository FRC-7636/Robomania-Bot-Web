# coding=utf-8
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404

from .models import DMeeting


# Create your views here.
@login_required
def index(request, meeting_id):
    meeting = get_object_or_404(DMeeting, pk=meeting_id)
    return render(request, 'Meetings/index.html',
                  {"meeting": meeting,
                   "can_edit": request.user.has_perm("Meetings.change_DMeeting") and request.user.has_perm(
                       "Meetings.delete_DMeeting")
                   })


@permission_required(["Meetings.change_DMeeting", "Meetings.delete_DMeeting"], raise_exception=True)
def edit(request, meeting_id):
    meeting = get_object_or_404(DMeeting, pk=meeting_id)
    return render(request, 'Meetings/edit.html', {"meeting": meeting})

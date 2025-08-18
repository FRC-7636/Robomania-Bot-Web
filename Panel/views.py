# coding=utf-8
from django.shortcuts import render
import datetime
from zoneinfo import ZoneInfo

from Meetings.models import DMeeting


TAIPEI_TZ = ZoneInfo("Asia/Taipei")


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        # Fetch meetings from the last two weeks and the next two weeks
        now = datetime.datetime.now(tz=TAIPEI_TZ)
        two_weeks_ago = (now - datetime.timedelta(weeks=2)).replace(tzinfo=TAIPEI_TZ)
        two_weeks_ahead = (now + datetime.timedelta(weeks=2)).replace(tzinfo=TAIPEI_TZ)
        upcoming_meetings = DMeeting.objects.filter(start_time__range=(now, two_weeks_ahead)).order_by("start_time")
        past_meetings = DMeeting.objects.filter(end_time__range=(two_weeks_ago, now)).order_by("-end_time")
        recent_warn_history = request.user.warning_history.order_by("-time")[:5]
        return render(
            request,
            'Panel/index.html',
            {
                "upcoming_meetings": upcoming_meetings,
                "past_meetings": past_meetings,
                "recent_warn_history": recent_warn_history
            }
        )
    else:
        return render(request, 'home.html')

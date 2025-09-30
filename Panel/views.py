# coding=utf-8
from django.shortcuts import render
import datetime
from zoneinfo import ZoneInfo
from markdown import Markdown
from io import StringIO

from Announcements.models import Announcement
from Meetings.models import DMeeting


TAIPEI_TZ = ZoneInfo("Asia/Taipei")


def unmark_element(element, stream=None):
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        unmark_element(sub, stream)
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()


# patching Markdown
Markdown.output_formats["plain"] = unmark_element  # noqa
__md = Markdown(output_format="plain")  # noqa
__md.stripTopLevelTags = False


def unmark(text):
    return __md.convert(text)


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        pinned_announcements = Announcement.objects.filter(is_pinned=True)
        pinned_announcements_condensed = []
        for ann in pinned_announcements:
            title = ann.title
            if len(title) > 15:
                title = title[:12] + "..."
            pinned_announcements_condensed.append({
                "id": ann.pk,
                "title": title,
                "content": unmark(ann.content).replace("\n", " "),
            })
        # Fetch meetings from the last two weeks and the next two weeks
        now = datetime.datetime.now(tz=TAIPEI_TZ)
        two_weeks_ago = (now - datetime.timedelta(weeks=2)).replace(tzinfo=TAIPEI_TZ)
        two_weeks_ahead = (now + datetime.timedelta(weeks=2)).replace(tzinfo=TAIPEI_TZ)
        upcoming_meetings = DMeeting.objects.filter(start_time__range=(now, two_weeks_ahead)).order_by("start_time")
        past_meetings = (DMeeting.objects.filter(start_time__lt=now, end_time__range=(two_weeks_ago, now))
                         .order_by("-end_time"))
        recent_warn_history = request.user.warning_history.order_by("-time")[:5]
        return render(
            request,
            'Panel/index.html',
            {
                "pinned_announcements": pinned_announcements_condensed,
                "upcoming_meetings": upcoming_meetings,
                "past_meetings": past_meetings,
                "recent_warn_history": recent_warn_history
            }
        )
    else:
        return render(request, 'home.html')

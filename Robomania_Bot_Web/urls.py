# coding=utf-8
"""
URL configuration for Robomania-Bot-Web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf.urls.static import static
from django.conf import settings

from rest_framework import routers
from debug_toolbar.toolbar import debug_toolbar_urls

from Meetings.views import MeetingsViewSet, AbsentRequestsViewSet
from Members.views import MembersViewSet
from Announcements.views import AnnouncementsViewSet

router = routers.DefaultRouter()
router.register(r"meetings", MeetingsViewSet)
router.register(r"members", MembersViewSet)
router.register(r"absent_requests", AbsentRequestsViewSet)
router.register(r"announcements", AnnouncementsViewSet)

urlpatterns = ([
    re_path(r'^$', include("Panel.urls")),
    path('admin/', admin.site.urls),
    path("member/", include("Members.urls")),
    path("meeting/", include("Meetings.urls")),
    path("accounts/", include("Auth.urls")),
    path("upload/", include("Uploader.urls")),
    path("user_uploads/", include("Uploader.urls_user_uploads")),
    path("announcement/", include("Announcements.urls")),
    path("api/", include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)) + debug_toolbar_urls()


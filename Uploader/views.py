# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.conf import settings
from django.utils.http import content_disposition_header
from magika import Magika
from uuid import uuid4
from os import remove

from .models import UserFile, UserFileForm


MAGIKA = Magika()
TEMP_DIR = settings.BASE_DIR / "temp"


# Create your views here.
@login_required()
def index(request):
    if request.method == "POST":
        form = UserFileForm(request.POST, request.FILES)
        if request.FILES["file"].size > 100 * 1024 * 1024:
            return redirect(f"{reverse('upload_index')}?error=檔案大小超過 100 MB。")
        if form.is_valid():
            user_file = form.save(commit=False)
            user_file.uploader = request.user
            user_file.require_login = (
                request.POST.get("require_login", "false") == "true"
            )
            # get MIME type of the uploaded file
            file = request.FILES["file"]
            # save the file to a temporary location instead of reading it directly
            temp_path = TEMP_DIR / str(uuid4())
            with open(temp_path, "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            user_file.mimetype = MAGIKA.identify_path(temp_path).output.mime_type
            # delete the temporary file after getting the MIME type
            remove(temp_path)
            user_file.save()
            return redirect(f"{reverse('upload_index')}?success={str(user_file.uuid)}")
        else:
            return redirect(
                f"{reverse('upload_index')}?error=未知錯誤，請檢查託管設定。"
            )
    return render(request, "Uploader/index.html")


def download(request, uuid):
    user_file = get_object_or_404(UserFile, uuid=uuid)
    if user_file.require_login and not request.user.is_authenticated:
        response = HttpResponse(status=404)
    else:
        response = HttpResponse(content_type=user_file.mimetype)
        response["Content-Disposition"] = content_disposition_header(
            as_attachment=user_file.mimetype == "application/octet-stream",
            filename=user_file.name,
        )
        response["X-Accel-Redirect"] = user_file.file.url
    return response

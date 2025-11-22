# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.conf import settings
from django.core.files import File
from django.utils.http import content_disposition_header
from django.contrib.auth.hashers import make_password, check_password

from magika import Magika, ContentTypeInfo
from uuid import uuid4
from os import remove
from PIL import Image
import io

from .models import UserFile, UserFileForm, MDImage, MDImageForm

MAGIKA = Magika()
TEMP_DIR = settings.BASE_DIR / "temp"


def get_file_type(file: File) -> ContentTypeInfo:
    # save the file to a temporary location instead of reading it directly
    temp_path = TEMP_DIR / str(uuid4())
    with open(temp_path, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    result = MAGIKA.identify_path(temp_path).output
    remove(temp_path)
    return result


def image_to_webp(original: File) -> File:
    img = Image.open(original)
    output = io.BytesIO()
    img.save(output, format="WEBP")
    output.seek(0)
    return File(output, name=f"{original.name.rsplit('.', 1)[0]}.webp")


# Create your views here.
@login_required()
def uploader_upload(request):
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
            require_password = request.POST.get("require_password", "false") == "true"
            if require_password:
                user_file.require_password = True
                password = request.POST.get("password", "")
                if password == "":
                    return redirect(f"{reverse('upload_index')}?error=請輸入密碼。")
                if len(password) < 6:
                    return redirect(f"{reverse('upload_index')}?error=密碼長度需至少 6 個字元。")
                user_file.password = make_password(password)
            user_file.mimetype = get_file_type(request.FILES["file"]).mime_type
            user_file.save()
            return redirect(f"{reverse('uploader_upload')}?success={str(user_file.uuid)}")
        else:
            return redirect(
                f"{reverse('uploader_upload')}?error=未知錯誤，請檢查託管設定。"
            )
    return render(request, "Uploader/index.html")


def uploader_download(request, uuid):
    user_file = get_object_or_404(UserFile, uuid=uuid)
    if request.method == "DELETE":
        if request.user.has_perm("Uploader.delete_userfile"):
            user_file.file.delete(save=False)
            user_file.delete()
            return HttpResponse(status=204)
        else:
            return HttpResponseForbidden()
    if user_file.require_login and not request.user.is_authenticated:
        response = redirect(f"{reverse('login')}?next={request.path}")
    elif user_file.require_password:
        if request.method == "POST":
            password = request.POST.get("password", "")
            if check_password(password, user_file.password):
                response = HttpResponse(content_type=user_file.mimetype)
                response["Content-Disposition"] = content_disposition_header(
                    as_attachment=user_file.mimetype == "application/octet-stream",
                    filename=user_file.name,
                )
                response["X-Accel-Redirect"] = user_file.file.url
            else:
                return render(
                    request,
                    "Uploader/password.html",
                    {"file_uuid": user_file.uuid, "error": "密碼錯誤，請重新輸入。"},
                )
        else:
            return render(request, "Uploader/password.html", {"file_uuid": user_file.uuid})
    else:
        response = HttpResponse(content_type=user_file.mimetype)
        response["Content-Disposition"] = content_disposition_header(
            as_attachment=user_file.mimetype == "application/octet-stream",
            filename=user_file.name,
        )
        response["X-Accel-Redirect"] = user_file.file.url
    return response


@login_required()
def mdimage_upload(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    form = MDImageForm(request.POST, request.FILES)
    if form.is_valid():
        md_image: MDImage = form.save(commit=False)
        md_image.uploader = request.user
        # check the file before saving
        file = request.FILES["image"]
        # limit file size to 2 MB
        if file.size > 2 * 1024 * 1024:
            return HttpResponse('{"error":"fileTooLarge"}', content_type="application/json", status=413)
        file_type = get_file_type(file).group
        if file_type != "image":
            return HttpResponse('{"error":"typeNotAllowed"}', content_type="application/json", status=415)
        converted_img = image_to_webp(file)
        md_image.image.save(converted_img.name, converted_img)
        md_image.save()
        return HttpResponse(
            f'{{"data":{{"filePath":"user_uploads/mdimages/{md_image.uuid}.webp"}}}}',
            content_type="application/json",
            status=200,
        )
    return HttpResponse('{"error":"typeNotAllowed"}', content_type="application/json", status=415)


def mdimage_download(request, uuid):
    md_image = get_object_or_404(MDImage, uuid=uuid)
    response = HttpResponse(content_type="image/webp")
    response["X-Accel-Redirect"] = md_image.image.url
    return response

# coding=utf-8
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from os import getenv  # noqa

from Members.models import DMember
from .discord_auth import *


# Create your views here.
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("discord_id")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            return render(
                request,
                "Auth/login.html",
                {
                    "error": "提供的 Discord ID 或密碼不正確。",
                    "cb_url": getenv("DISCORD_LOGIN_CALLBACK_URL"),
                },
            )
    else:  # GET
        if request.user.is_authenticated:
            return redirect("/")
        else:
            if request.GET.get("error", None):
                return render(
                    request,
                    "Auth/login.html",
                    {
                        "error": request.GET.get("error", None),
                        "cb_url": getenv("DISCORD_LOGIN_CALLBACK_URL"),
                    },
                )
            elif request.GET.get("success", None):
                return render(
                    request,
                    "Auth/login.html",
                    {"success": request.GET.get("success", None)},
                )
            return render(
                request,
                "Auth/login.html",
                {"cb_url": getenv("DISCORD_LOGIN_CALLBACK_URL")},
            )


def discord_login_view(request):
    code = request.GET.get("code", None)
    if code:
        response = get_access_token_response(
            getenv("DISCORD_CLIENT_ID"),
            getenv("DISCORD_CLIENT_SECRET"),
            code,
        )
        access_token, refresh_token = (
            response["access_token"],
            response["refresh_token"],
        )
        user_info = get_user_info(access_token)
        # check if user is already exists
        discord_id = user_info["id"]
        if DMember.objects.filter(discord_id=discord_id).exists():
            user = DMember.objects.get(discord_id=discord_id)
            # login the user
            login(request, user)
            return redirect("/")
        else:
            access_token = refresh_access_token(
                getenv("DISCORD_CLIENT_ID"),
                getenv("DISCORD_CLIENT_SECRET"),
                refresh_token,
            )["access_token"]
            guild_ids = get_user_guild_ids(access_token)
            # 檢查是否已加入 FRC# 7636 的 Discord 伺服器
            if 1114203090950836284 in guild_ids:
                return register_view(request, user_info)
            else:
                return redirect(
                    "/accounts/login/?error=此 Discord 帳號尚未加入 FRC# 7636 的 Discord 伺服器。"
                )
    else:
        return redirect("/accounts/login/?error=Discord 授權失敗，請重新登入。")


@login_required
def logout_view(request):
    logout(request)
    return redirect("/accounts/login/")


def register_view(request, user_info=None):
    if request.method == "POST":
        DMember.objects.create_user(
            discord_id=request.POST.get("discord_id"),
            real_name=request.POST.get("real_name"),
            email_address=request.POST.get("email_address"),
            avatar=request.POST.get("avatar_url"),
            password=request.POST.get("password"),
        )
        return redirect(
            "/accounts/login/?success=註冊成功。你現在可以使用 Discord 登入，或使用密碼登入。"
        )
    else:  # GET
        if not request.user.is_authenticated:
            if user_info is not None:
                condensed_user_info = {
                    "discord_id": user_info["id"],
                    "email_address": user_info["email"],
                    "avatar_url": f"https://cdn.discordapp.com/avatars/{user_info['id']}/{user_info['avatar']}.png"
                    f"?size=256",
                }
                return render(
                    request, "Auth/register.html", {"user_info": condensed_user_info}
                )
            else:  # User accessed this view without Discord auth
                return HttpResponse(
                    "Bad Request: register_view should not be called without Discord auth.",
                    status=400,
                )
        else:
            return redirect("/")  # Redirect to home if user is already authenticated


@login_required
def password_change_view(request):
    if request.method == "POST":
        if request.user.check_password(request.POST.get("old-password", None)):
            request.user.set_password(request.POST.get("new-password", None))
            request.user.save()
            logout(request)
            return redirect("/accounts/login/?success=密碼修改成功，請重新登入。")
        else:
            return redirect("/accounts/password_change/?error=提供的密碼錯誤。")
    else:
        return render(request, "Auth/password_change.html")


@login_required
def sync_avatar_view(request):
    code = request.GET.get("code", None)
    if code:
        response = get_access_token_response(
            getenv("DISCORD_CLIENT_ID"),
            getenv("DISCORD_CLIENT_SECRET"),
            code,
            redirect_uri_suffix="/accounts/sync_avatar/",
            scope="identify",
        )
        access_token = response["access_token"]
        user_info = get_user_info(access_token)
        if str(request.user.discord_id) == user_info["id"]:
            request.user.avatar = (
                f"https://cdn.discordapp.com/avatars/{user_info['id']}/{user_info['avatar']}"
                f".png?size=256"
            )
            request.user.save()
        return redirect("/")
    else:
        return redirect(
            f"https://discord.com/oauth2/authorize?client_id=1402621019432157266&response_type=code&prompt=none"
            f"&redirect_uri={getenv("DISCORD_LOGIN_CALLBACK_URL")}%2Faccounts%2Fsync_avatar%2F&scope=identify"
        )

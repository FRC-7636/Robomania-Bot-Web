# coding=utf-8
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.shortcuts import render, redirect
from os import getenv  # noqa
from random import randint

from Members.models import DMember
from .discord_auth import DiscordAuth


def to_next_page(request):
    next_url = request.session.get("next", None)
    if next_url:
        del request.session["next"]
        return next_url
    return "/"


def pick_avatar_from_aobuta() -> str:
    base_url = "https://ao-buta.com/santa/special/icon_50/img/"
    icon_amount = {
        1: 6,
        2: 9,
        3: 6,
        4: 6,
        5: 6,
        6: 6,
        7: 6,
    }
    icon_char = randint(1, 7)
    icon_num = randint(1, icon_amount[icon_char])
    return base_url + f"icon_0{icon_char}_{icon_num}.jpg"


# Create your views here.
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("discord_id")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(to_next_page(request))
        else:
            return render(
                request,
                "Auth/login.html",
                {
                    "error": "提供的 Discord ID 或密碼不正確。",
                },
            )
    else:  # GET
        request.session["next"] = request.GET.get("next", None)
        if request.user.is_authenticated:
            return redirect(to_next_page(request))
        else:
            if request.GET.get("error", None):
                return render(
                    request,
                    "Auth/login.html",
                    {
                        "error": request.GET.get("error", None),
                    },
                )
            elif request.GET.get("success", None):
                return render(
                    request,
                    "Auth/login.html",
                    {
                        "success": request.GET.get("success", None),
                    },
                )
            return render(
                request,
                "Auth/login.html",
            )


def discord_login_view(request):
    code = request.GET.get("code", None)
    if code:
        dc_auth_obj = DiscordAuth(
            getenv("DISCORD_CLIENT_ID"), getenv("DISCORD_CLIENT_SECRET"),
            f"{'http' if request.get_host() == '127.0.0.1' else 'https'}://{request.get_host()}"
        )
        dc_auth_obj.update_access_token(code)
        user_info = dc_auth_obj.get_user_info()
        # check if user is already exists
        discord_id = user_info["id"]
        if (
            DMember.objects.filter(discord_id=discord_id).exists()
            and DMember.objects.get(discord_id=discord_id).password != ""
        ):
            user = DMember.objects.get(discord_id=discord_id)
            # login the user
            login(request, user)
            return redirect(to_next_page(request))
        else:
            guild_ids = dc_auth_obj.get_user_guild_ids()
            # 檢查是否已加入 FRC# 7636 的 Discord 伺服器
            if 1114203090950836284 in guild_ids:
                return register_view(request, user_info)
            else:
                return redirect(
                    "/accounts/login/?error=此 Discord 帳號尚未加入 FRC #7636 的 Discord 伺服器。"
                )
    else:
        return redirect("/accounts/login/?error=Discord 授權失敗，請重新登入。")


@login_required
def logout_view(request):
    logout(request)
    return redirect("/accounts/login/")


def register_view(request, user_info=None):
    if request.method == "POST":
        if not DMember.objects.filter(
            discord_id=request.POST.get("discord_id")
        ).exists():
            DMember.objects.create_user(
                discord_id=request.POST.get("discord_id"),
                real_name=request.POST.get("real_name"),
                email_address=request.POST.get("email_address"),
                avatar=request.POST.get("avatar_url"),
                password=request.POST.get("password"),
            )
        elif DMember.objects.get(discord_id=request.POST.get("discord_id")).password == "":
            member_obj = DMember.objects.get(discord_id=request.POST.get("discord_id"))
            member_obj.real_name = request.POST.get("real_name")
            member_obj.email_address = request.POST.get("email_address")
            member_obj.avatar = request.POST.get("avatar_url")
            member_obj.password = make_password(request.POST.get("password"))
            member_obj.save()
        return redirect(
            "/accounts/login/?success=註冊成功。你現在可以使用 Discord 登入，或使用密碼登入。"
        )
    else:  # GET
        if not request.user.is_authenticated:
            if user_info is not None:
                if user_info["avatar"] is None:
                    avatar_url = pick_avatar_from_aobuta()
                else:
                    avatar_url = (f"https://cdn.discordapp.com/avatars/{user_info['id']}/{user_info['avatar']}.png"
                                  "?size=256")
                condensed_user_info = {
                    "discord_id": user_info["id"],
                    "email_address": user_info["email"],
                    "avatar_url": avatar_url,
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
        dc_auth_obj = DiscordAuth(
            getenv("DISCORD_CLIENT_ID"), getenv("DISCORD_CLIENT_SECRET"),
            f"{'http' if request.get_host() == '127.0.0.1' else 'https'}://{request.get_host()}"
        )
        dc_auth_obj.update_access_token(
            code, redirect_uri_suffix="/accounts/sync_avatar/", scope="identify"
        )
        user_info = dc_auth_obj.get_user_info()
        if str(request.user.discord_id) == user_info["id"]:
            request.user.avatar = (
                f"https://cdn.discordapp.com/avatars/{user_info['id']}/{user_info['avatar']}"
                f".png?size=256"
            )
            request.user.save()
            return redirect("/?sync=success")
        return redirect("/?sync=failed")
    else:
        return redirect(
            f"https://discord.com/oauth2/authorize?client_id=1402621019432157266&response_type=code&prompt=none"
            f"&redirect_uri={'http' if request.get_host() == '127.0.0.1' else 'https'}%3A%2F%2F{request.get_host()}"
            f"%2Faccounts%2Fsync_avatar%2F&scope=identify"
        )

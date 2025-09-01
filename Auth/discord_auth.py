# coding=utf-8
import requests
from os import getenv
from urllib.parse import unquote
from pprint import pprint


def get_access_token_response(client_id: int | str, client_secret: str, code: str,
                              redirect_uri_suffix="/accounts/login/discord/",
                              scope="identify email guilds") -> dict:
    """
    Get access token from Discord using the provided client ID, client secret, and authorization code.
    """
    url = "https://discord.com/api/oauth2/token"
    data = {
        'client_id': str(client_id),
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': f'{unquote(getenv("DISCORD_LOGIN_CALLBACK_URL"))}{redirect_uri_suffix}',
        'scope': scope
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get access token: {response.text}")


def refresh_access_token(client_id: int | str, client_secret: str, refresh_token: str) -> dict:
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    url = "https://discord.com/api/v10/oauth2/token"
    response = requests.post(url, data=data, headers=headers, auth=(str(client_id), client_secret))
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to refresh access token: {response.text}")


def get_user_info(access_token: str) -> dict:
    """
    Get user information from Discord using the provided access token.
    """
    url = "https://discord.com/api/v10/users/@me"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get user info: {response.text}")


def get_user_guild_ids(access_token: str) -> list[int]:
    """
    Get user guilds from Discord using the provided access token.
    """
    url = "https://discord.com/api/v10/users/@me/guilds"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        servers = response.json()
        guild_ids = []
        for server in servers:
            guild_ids.append(int(server["id"]))
        return guild_ids
    else:
        raise Exception(f"Failed to get user guilds: {response.text}")


if __name__ == '__main__':
    from dotenv import load_dotenv
    from os import getenv

    load_dotenv("CONFIG.env")
    n_access_token = refresh_access_token(
        getenv("DISCORD_CLIENT_ID"),
        getenv("DISCORD_CLIENT_SECRET"),
        "pDWeGOhOto4Xj4Ki9X3s2SB6RnSD9r"
    )
    print(n_access_token.get('access_token'))
    print(n_access_token.get('refresh_token'))
    result = get_user_guild_ids(n_access_token.get('access_token'))
    pprint(result)

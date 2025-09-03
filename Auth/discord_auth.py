# coding=utf-8
import requests
from os import getenv
from urllib.parse import unquote


class DiscordAuth:
    def __init__(self, client_id: int | str, client_secret: str):
        self.client_id = str(client_id)
        self.client_secret = client_secret
        self.access_token = None
        self.refresh_token = None

    def update_access_token(self, code: str = None,
                            redirect_uri_suffix="/accounts/login/discord/",
                            scope="identify email guilds"):
        if self.refresh_token is None:
            if code is None:
                raise ValueError("Either code or refresh_token must be provided.")
            url = "https://discord.com/api/oauth2/token"
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": f'{unquote(getenv("DISCORD_LOGIN_CALLBACK_URL"))}{redirect_uri_suffix}',
                "scope": scope,
            }

            response = requests.post(url, data=data)
        else:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
            }
            url = "https://discord.com/api/v10/oauth2/token"
            response = requests.post(
                url, data=data, headers=headers, auth=(self.client_id, self.client_secret)
            )
        if response.status_code == 200:
            self.access_token = response.json().get("access_token", None)
            self.refresh_token = response.json().get("refresh_token", None)
        else:
            raise Exception(f"Failed to update access token: {response.text}")

    def get_user_info(self) -> dict:
        """
        Get user information from Discord using the provided access token.
        """
        if self.access_token is None:
            self.update_access_token()
        url = "https://discord.com/api/v10/users/@me"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        self.access_token = None
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get user info: {response.text}")

    def get_user_guild_ids(self) -> list[int]:
        """
        Get user guilds from Discord using the provided access token.
        """
        if self.access_token is None:
            self.update_access_token()
        url = "https://discord.com/api/v10/users/@me/guilds"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            servers = response.json()
            guild_ids = []
            for server in servers:
                guild_ids.append(int(server["id"]))
            return guild_ids
        else:
            raise Exception(f"Failed to get user guilds: {response.text}")


def get_access_token_response(
    client_id: int | str,
    client_secret: str,
    code: str,
    redirect_uri_suffix="/accounts/login/discord/",
    scope="identify email guilds",
) -> dict:
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
    from pprint import pprint

    load_dotenv("../CONFIG.env")
    test_obj = DiscordAuth(
        getenv("DISCORD_CLIENT_ID"),
        getenv("DISCORD_CLIENT_SECRET"))
    test_obj.update_access_token("JTZPGu9QuSEstGaRsKkAXAMV1uQk4d")
    pprint(test_obj.get_user_info())
    pprint(test_obj.get_user_guild_ids())

# coding=utf-8
import requests


class DiscordAuth:
    def __init__(
        self,
        client_id: int | str = None,
        client_secret: str = None,
        host: str = None,
        api_middleware_url: str = None,
        middleware_token: str = None,
    ):
        self.client_id = str(client_id)
        self.client_secret = client_secret
        self.access_token = None
        self.refresh_token = None
        self.host = host
        self.api_middleware_url = api_middleware_url
        if api_middleware_url:
            self.middleware_token_header = {"X-API-Token": middleware_token}
        else:
            self.middleware_token_header = None

    def update_access_token(
        self,
        code: str = None,
        redirect_uri_suffix="/accounts/login/discord/",
        scope="identify email guilds",
    ):
        if not (self.client_id and self.client_secret):
            raise ValueError("client_id and client_secret must be provided.")
        url = "https://discord.com/api/v10/oauth2/token"
        if self.refresh_token is None:
            if code is None:
                raise ValueError("Either code or refresh_token must be provided.")
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": f"{self.host}{redirect_uri_suffix}",
                "scope": scope,
            }

            response = requests.post(
                self.api_middleware_url,
                json={
                    "method": "POST",
                    "url": url,
                    "data": data,
                },
                auth=(self.client_id, self.client_secret),
                headers=self.middleware_token_header,
            ) if self.api_middleware_url else requests.post(url, data=data, auth=(self.client_id, self.client_secret))
        else:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
            }
            response = (
                requests.post(
                    self.api_middleware_url,
                    json={
                        "method": "POST",
                        "url": url,
                        "data": data,
                    },
                    auth=(self.client_id, self.client_secret),
                    headers=self.middleware_token_header,
                )
                if self.api_middleware_url
                else (
                    requests.post(
                        url,
                        data=data,
                        headers=headers,
                        auth=(self.client_id, self.client_secret),
                    )
                )
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
        response = (
            requests.post(
                self.api_middleware_url,
                json={
                    "method": "GET",
                    "url": url,
                    "headers": headers,
                },
                headers=self.middleware_token_header,
            )
            if self.api_middleware_url
            else requests.get(url, headers=headers)
        )
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
        response = (
            requests.post(
                self.api_middleware_url,
                json={
                    "method": "GET",
                    "url": url,
                    "headers": headers,
                },
                headers=self.middleware_token_header,
            )
            if self.api_middleware_url
            else requests.get(url, headers=headers)
        )
        if response.status_code == 200:
            servers = response.json()
            guild_ids = []
            for server in servers:
                guild_ids.append(int(server["id"]))
            return guild_ids
        else:
            raise Exception(f"Failed to get user guilds: {response.text}")

    def send_request_via_middleware(self, method: str, url: str, headers: dict = None, data: dict = None):
        """
        Send a request via the API middleware.
        """
        if self.api_middleware_url is None or self.middleware_token_header is None:
            raise ValueError("API middleware URL or Token is not set.")
        response = requests.post(
            self.api_middleware_url,
            json={
                "method": method,
                "url": url,
                "headers": headers,
                "data": data,
            },
            headers=self.middleware_token_header,
        )
        return response


if __name__ == "__main__":
    from dotenv import load_dotenv
    from os import getenv
    from pprint import pprint

    load_dotenv("CONFIG.env")
    test_obj = DiscordAuth(
        getenv("DISCORD_CLIENT_ID"),
        getenv("DISCORD_CLIENT_SECRET"),
        api_middleware_url=getenv("DISCORD_API_MIDDLEWARE_URL"),
    )
    test_obj.update_access_token("65ceT95WaInweqklUsntI1U8ugrDH9")
    pprint(test_obj.get_user_info())
    pprint(test_obj.get_user_guild_ids())

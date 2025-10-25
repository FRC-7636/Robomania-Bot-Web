# coding=utf-8
from django import template
from datetime import timedelta

register = template.Library()


@register.filter("to_dc_format")
def to_dc_format(location: str, channel_dict: dict) -> str:
    if location.startswith("dc-"):
        channel_id = int(location[3:])
        for category, channels in channel_dict.items():
            for channel in channels:
                if channel["id"] == channel_id:
                    channel_name = f"{category}/{channel['name']}"
                    link = f"discord://-/channels/1114203090950836284/{channel_id}"
                    backup_link = f"https://discord.com/channels/1114203090950836284/{channel_id}"
                    return f"""
                    <div class="discord-vc-channel">
                    <a href="{link}" target="_blank" rel="noopener noreferrer" style="text-decoration: none;">
                    Discord - {channel_name}
                    </a>
                    &nbsp;
                    <a href="{backup_link}" target="_blank" rel="noopener noreferrer" style="font-style: italic;">
                    (於瀏覽器開啟)
                    </a>
                    </div>
                    """
    return location

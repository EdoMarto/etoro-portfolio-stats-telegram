"""Minimal Telegram Bot API client: a text message and a group of photos."""

from __future__ import annotations

import json

import requests

_TIMEOUT = 60


def _url(token: str, method: str) -> str:
    return f"https://api.telegram.org/bot{token}/{method}"


def send_message(token: str, chat_id: str, text: str) -> None:
    response = requests.post(
        _url(token, "sendMessage"),
        json={"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True},
        timeout=_TIMEOUT,
    )
    response.raise_for_status()


def send_photo_group(token: str, chat_id: str, image_paths: list[str], caption: str | None = None) -> None:
    """Send up to 10 images as a single album. Caption goes on the first one."""
    if not image_paths:
        return

    media = []
    files = {}
    try:
        for index, path in enumerate(image_paths[:10]):
            key = f"photo{index}"
            files[key] = open(path, "rb")
            item = {"type": "photo", "media": f"attach://{key}"}
            if index == 0 and caption:
                item["caption"] = caption
                item["parse_mode"] = "HTML"
            media.append(item)

        response = requests.post(
            _url(token, "sendMediaGroup"),
            data={"chat_id": chat_id, "media": json.dumps(media)},
            files=files,
            timeout=_TIMEOUT,
        )
        response.raise_for_status()
    finally:
        for handle in files.values():
            handle.close()

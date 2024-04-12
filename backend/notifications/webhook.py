"""Webhook notification channel."""
import json
from backend.notifications.base import NotificationChannel

class WebhookChannel(NotificationChannel):
    def __init__(self, url: str):
        self.url = url

    def send(self, message: str) -> bool:
        try:
            import httpx
            httpx.post(self.url, json={"text": message, "source": "OdaTrade"}, timeout=5)
            return True
        except Exception:
            return False

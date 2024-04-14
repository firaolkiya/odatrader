"""Telegram notification channel."""
from backend.notifications.base import NotificationChannel

class TelegramChannel(NotificationChannel):
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send(self, message: str) -> bool:
        try:
            import httpx
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            httpx.post(url, json={"chat_id": self.chat_id, "text": f"[OdaTrade] {message}"}, timeout=5)
            return True
        except Exception:
            return False

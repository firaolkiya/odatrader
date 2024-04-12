"""Email notification channel."""
from backend.notifications.base import NotificationChannel

class EmailChannel(NotificationChannel):
    def __init__(self, smtp_host: str, to_addr: str):
        self.smtp_host = smtp_host
        self.to_addr = to_addr

    def send(self, message: str) -> bool:
        # Stub: log only in dev
        print(f"[OdaTrade Email] To {self.to_addr}: {message[:100]}")
        return True

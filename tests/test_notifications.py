import pytest
from backend.notifications.base import NotificationDispatcher
from backend.notifications.email_channel import EmailChannel

class TestNotificationDispatcher:
    def test_add_channel(self):
        d = NotificationDispatcher()
        d.add_channel(EmailChannel("smtp", "test@test.com"))
        assert len(d.channels) == 1

    def test_dispatch(self):
        d = NotificationDispatcher()
        d.add_channel(EmailChannel("smtp", "test@test.com"))
        results = d.dispatch("test message")
        assert results

class TestEmailChannel:
    def test_send(self):
        ch = EmailChannel("smtp", "test@test.com")
        assert ch.send("hello") is True

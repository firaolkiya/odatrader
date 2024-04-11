"""Notification dispatcher."""
from typing import List
from abc import ABC, abstractmethod

class NotificationChannel(ABC):
    @abstractmethod
    def send(self, message: str) -> bool:
        pass

class NotificationDispatcher:
    def __init__(self):
        self.channels: List[NotificationChannel] = []

    def add_channel(self, channel: NotificationChannel):
        self.channels.append(channel)

    def dispatch(self, message: str):
        return {type(c).__name__: c.send(message) for c in self.channels}

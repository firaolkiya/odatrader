"""Configurable alert engine."""
from typing import List, Callable
from backend.notifications.base import NotificationDispatcher

class AlertEngine:
    def __init__(self, dispatcher: NotificationDispatcher):
        self.dispatcher = dispatcher
        self.rules: List[dict] = []

    def add_rule(self, name: str, condition: Callable, message: str):
        self.rules.append({"name": name, "condition": condition, "message": message})

    def evaluate(self, context: dict):
        for rule in self.rules:
            if rule["condition"](context):
                self.dispatcher.dispatch(f"[{rule['name']}] {rule['message']}")

"""Simple pub/sub event bus."""
from collections import defaultdict
from typing import Callable, Any, List

class EventBus:
    def __init__(self):
        self._handlers = defaultdict(list)

    def subscribe(self, event: str, handler: Callable[[Any], None]):
        self._handlers[event].append(handler)

    def publish(self, event: str, data: Any = None):
        for handler in self._handlers[event]:
            handler(data)

    def clear(self, event: str = None):
        if event:
            self._handlers[event].clear()
        else:
            self._handlers.clear()

bus = EventBus()

"""Async event bus with pluggable backends (Redis, Kafka, NATS, in-memory)."""
import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger("odatrade.eventbus")


class EventType(str, Enum):
    MARKET_DATA = "market_data"
    FEATURES_READY = "features_ready"
    STRATEGY_SIGNAL = "strategy_signal"
    RISK_CHECK = "risk_check"
    RISK_APPROVED = "risk_approved"
    RISK_REJECTED = "risk_rejected"
    ORDER_CREATED = "order_created"
    ORDER_FILLED = "order_filled"
    ORDER_CANCELLED = "order_cancelled"
    PNL_UPDATE = "pnl_update"
    KILL_SWITCH = "kill_switch"
    BOT_STARTED = "bot_started"
    BOT_STOPPED = "bot_stopped"
    NEWS_SENTIMENT = "news_sentiment"
    HEALTH_CHECK = "health_check"


@dataclass
class Event:
    type: EventType
    bot_id: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    correlation_id: str = ""

    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "bot_id": self.bot_id,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, data: dict) -> "Event":
        return cls(
            type=EventType(data["type"]),
            bot_id=data["bot_id"],
            payload=data.get("payload", {}),
            timestamp=data.get("timestamp", ""),
            correlation_id=data.get("correlation_id", ""),
        )

    @classmethod
    def from_json(cls, raw: str) -> "Event":
        return cls.from_dict(json.loads(raw))


Handler = Callable[[Event], Any]


class EventBackend(ABC):
    @abstractmethod
    async def publish(self, event: Event) -> bool:
        pass

    @abstractmethod
    async def subscribe(self, event_type: EventType, handler: Handler):
        pass

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass


class InMemoryBackend(EventBackend):
    """In-process event bus for single-node / dev."""

    def __init__(self):
        self._handlers: Dict[EventType, List[Handler]] = {}
        self._running = False

    async def publish(self, event: Event) -> bool:
        handlers = self._handlers.get(event.type, [])
        for h in handlers:
            try:
                result = h(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error("Handler error for %s: %s", event.type, e)
        return True

    async def subscribe(self, event_type: EventType, handler: Handler):
        self._handlers.setdefault(event_type, []).append(handler)

    async def start(self):
        self._running = True

    async def stop(self):
        self._running = False


class RedisBackend(EventBackend):
    """Redis pub/sub backend for multi-process event distribution."""

    def __init__(self, redis_client, channel_prefix: str = "odatrade:bus:"):
        self.redis = redis_client
        self.prefix = channel_prefix
        self._handlers: Dict[EventType, List[Handler]] = {}
        self._pubsub = None
        self._listener_task = None
        self._running = False

    def _channel(self, event_type: EventType) -> str:
        return f"{self.prefix}{event_type.value}"

    async def publish(self, event: Event) -> bool:
        if not self.redis.is_connected:
            return False
        channel = self._channel(event.type)
        self.redis.publish(channel, event.to_json())
        return True

    async def subscribe(self, event_type: EventType, handler: Handler):
        self._handlers.setdefault(event_type, []).append(handler)

    async def _listen(self):
        if not self.redis.is_connected:
            return
        channels = [self._channel(et) for et in self._handlers]
        if not channels:
            return
        self._pubsub = self.redis.client.pubsub()
        self._pubsub.subscribe(*channels)
        while self._running:
            message = self._pubsub.get_message(timeout=1.0)
            if message and message["type"] == "message":
                try:
                    event = Event.from_json(message["data"])
                    for h in self._handlers.get(event.type, []):
                        result = h(event)
                        if asyncio.iscoroutine(result):
                            await result
                except Exception as e:
                    logger.error("Redis listener error: %s", e)
            await asyncio.sleep(0.01)

    async def start(self):
        self._running = True
        if self.redis.is_connected:
            self._listener_task = asyncio.create_task(self._listen())

    async def stop(self):
        self._running = False
        if self._pubsub:
            self._pubsub.unsubscribe()
        if self._listener_task:
            self._listener_task.cancel()


class KafkaBackend(EventBackend):
    """Kafka backend stub for distributed scale-out."""

    def __init__(self, bootstrap_servers: str = "localhost:9092", topic_prefix: str = "odatrade"):
        self.bootstrap_servers = bootstrap_servers
        self.topic_prefix = topic_prefix
        self._handlers: Dict[EventType, List[Handler]] = {}
        self._producer = None
        self._consumer = None
        self._running = False

    def _topic(self, event_type: EventType) -> str:
        return f"{self.topic_prefix}.{event_type.value}"

    async def publish(self, event: Event) -> bool:
        try:
            from aiokafka import AIOKafkaProducer
            if self._producer is None:
                self._producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
                await self._producer.start()
            await self._producer.send_and_wait(self._topic(event.type), event.to_json().encode())
            return True
        except ImportError:
            logger.warning("aiokafka not installed; Kafka publish skipped")
            return False
        except Exception as e:
            logger.error("Kafka publish error: %s", e)
            return False

    async def subscribe(self, event_type: EventType, handler: Handler):
        self._handlers.setdefault(event_type, []).append(handler)

    async def start(self):
        self._running = True

    async def stop(self):
        self._running = False
        if self._producer:
            await self._producer.stop()


class NATSBackend(EventBackend):
    """NATS backend stub for lightweight distributed messaging."""

    def __init__(self, servers: str = "nats://localhost:4222", subject_prefix: str = "odatrade"):
        self.servers = servers
        self.subject_prefix = subject_prefix
        self._handlers: Dict[EventType, List[Handler]] = {}
        self._nc = None
        self._running = False

    def _subject(self, event_type: EventType) -> str:
        return f"{self.subject_prefix}.{event_type.value}"

    async def publish(self, event: Event) -> bool:
        try:
            import nats
            if self._nc is None:
                self._nc = await nats.connect(self.servers)
            await self._nc.publish(self._subject(event.type), event.to_json().encode())
            return True
        except ImportError:
            logger.warning("nats-py not installed; NATS publish skipped")
            return False
        except Exception as e:
            logger.error("NATS publish error: %s", e)
            return False

    async def subscribe(self, event_type: EventType, handler: Handler):
        self._handlers.setdefault(event_type, []).append(handler)

    async def start(self):
        self._running = True

    async def stop(self):
        self._running = False
        if self._nc:
            await self._nc.close()


class AsyncEventBus:
    """Facade over multiple event backends with fan-out publish."""

    def __init__(self, backends: List[EventBackend] = None):
        self.backends = backends or [InMemoryBackend()]
        self._handlers: Dict[EventType, List[Handler]] = {}
        self._started = False

    async def start(self):
        for backend in self.backends:
            await backend.start()
            for event_type, handlers in self._handlers.items():
                for h in handlers:
                    await backend.subscribe(event_type, h)
        self._started = True

    async def stop(self):
        for backend in self.backends:
            await backend.stop()
        self._started = False

    def on(self, event_type: EventType, handler: Handler):
        self._handlers.setdefault(event_type, []).append(handler)
        return handler

    async def emit(self, event: Event) -> bool:
        results = []
        for backend in self.backends:
            ok = await backend.publish(event)
            results.append(ok)
        return any(results)

    async def emit_market_data(self, bot_id: str, symbol: str, candle: dict, correlation_id: str = ""):
        return await self.emit(Event(
            type=EventType.MARKET_DATA, bot_id=bot_id,
            payload={"symbol": symbol, "candle": candle},
            correlation_id=correlation_id,
        ))

    async def emit_signal(self, bot_id: str, symbol: str, signal: str, strategy: str, correlation_id: str = ""):
        await self.emit(Event(
            type=EventType.STRATEGY_SIGNAL, bot_id=bot_id,
            payload={"symbol": symbol, "signal": signal, "strategy": strategy},
            correlation_id=correlation_id,
        ))

    async def emit_pnl(self, bot_id: str, symbol: str, pnl: float, cumulative: float, correlation_id: str = ""):
        await self.emit(Event(
            type=EventType.PNL_UPDATE, bot_id=bot_id,
            payload={"symbol": symbol, "pnl": pnl, "cumulative": cumulative},
            correlation_id=correlation_id,
        ))


def create_event_bus(backend: str = "redis", redis_url: str = None, **kwargs) -> AsyncEventBus:
    """Factory to create event bus with specified backend."""
    backends = [InMemoryBackend()]
    if backend == "redis" and redis_url:
        from odatrade.core.redis_client import RedisClient
        client = RedisClient.get_instance(redis_url)
        client.connect()
        backends.append(RedisBackend(client))
    elif backend == "kafka":
        backends.append(KafkaBackend(**kwargs))
    elif backend == "nats":
        backends.append(NATSBackend(**kwargs))
    return AsyncEventBus(backends)

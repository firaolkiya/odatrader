"""Configuration and input validators for OdaTrade."""
import re
from typing import List, Optional, Tuple

from odatrade.core.exceptions import ConfigError

VALID_SYMBOLS_PATTERN = re.compile(r"^[a-z]{3,10}usdt$")
VALID_INTERVALS = {"1m", "5m", "15m", "1h", "4h", "1d"}
VALID_RISK_PROFILES = {"conservative", "moderate", "aggressive"}
VALID_EVENT_BACKENDS = {"redis", "kafka", "nats", "memory"}


def validate_symbol(symbol: str) -> str:
    s = symbol.lower().strip()
    if not VALID_SYMBOLS_PATTERN.match(s):
        raise ConfigError(f"Invalid symbol format: {symbol}")
    return s


def validate_symbols(symbols: List[str]) -> List[str]:
    if not symbols:
        raise ConfigError("At least one symbol is required")
    if len(symbols) > 20:
        raise ConfigError("Maximum 20 symbols per bot")
    return [validate_symbol(s) for s in symbols]


def validate_interval(interval: str) -> str:
    if interval not in VALID_INTERVALS:
        raise ConfigError(f"Invalid interval: {interval}. Choose from {VALID_INTERVALS}")
    return interval


def validate_risk_profile(profile: str) -> str:
    if profile not in VALID_RISK_PROFILES:
        raise ConfigError(f"Invalid risk profile: {profile}")
    return profile


def validate_event_backend(backend: str) -> str:
    if backend not in VALID_EVENT_BACKENDS:
        raise ConfigError(f"Invalid event backend: {backend}")
    return backend


def validate_database_url(url: str) -> Tuple[bool, Optional[str]]:
    if not url:
        return False, "Database URL is empty"
    if url.startswith("sqlite"):
        return True, None
    if url.startswith("postgresql"):
        return True, None
    return False, f"Unsupported database URL scheme: {url.split(':')[0]}"


def validate_redis_url(url: str) -> Tuple[bool, Optional[str]]:
    if not url:
        return False, "Redis URL is empty"
    if url.startswith("redis://") or url.startswith("rediss://"):
        return True, None
    return False, "Redis URL must start with redis:// or rediss://"

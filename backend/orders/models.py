"""Order domain models."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    PARTIAL = "partial"

@dataclass
class Order:
    symbol: str
    side: OrderSide
    quantity: float
    price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    filled_qty: float = 0.0
    avg_fill_price: float = 0.0

"""Persistent decision logging: inputs → signals → fills."""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger("odatrade.audit")


class DecisionLogger:
    def __init__(self, log_dir: str = "logs/decisions"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._buffer: List[dict] = []

    def _write(self, event_type: str, data: dict):
        entry = {"type": event_type, "ts": datetime.now(timezone.utc).isoformat(), **data}
        self._buffer.append(entry)
        if len(self._buffer) >= 50:
            self.flush()

    def log_signal(self, snapshot):
        self._write("signal", snapshot.to_dict() if hasattr(snapshot, "to_dict") else snapshot)

    def log_order(self, intent, order, result: dict):
        self._write("order", {
            "intent": intent.to_dict() if hasattr(intent, "to_dict") else str(intent),
            "order_id": order.id, "result": result,
        })

    def log_fill(self, intent, order, result: dict):
        self._write("fill", {
            "instrument": intent.instrument, "side": intent.side,
            "fill_price": result.get("fill_price"), "fees": result.get("fees"),
            "order_id": order.id,
        })

    def log_reject(self, intent, reason: str):
        self._write("reject", {"instrument": intent.instrument, "reason": reason})

    def flush(self):
        if not self._buffer:
            return
        fname = self.log_dir / f"decisions_{datetime.now(timezone.utc).strftime('%Y%m%d')}.jsonl"
        with open(fname, "a") as f:
            for entry in self._buffer:
                f.write(json.dumps(entry, default=str) + "\n")
        self._buffer.clear()

    def recent(self, limit: int = 100) -> List[dict]:
        return self._buffer[-limit:]

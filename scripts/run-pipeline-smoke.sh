#!/usr/bin/env bash
# Smoke-test async event pipeline idempotency and dedup under bash orchestration.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "==> pipeline idempotency smoke"

python3 <<'PY'
import asyncio
from odatrade.core.event_bus_async import AsyncEventBus, Event, EventType
from backend.events.idempotency import EventDeduplicator

async def main():
    bus = AsyncEventBus()
    dedup = EventDeduplicator()
    fills = []

    async def on_approved(event):
        if dedup.is_duplicate(event):
            return
        dedup.mark(event)
        fills.append(event.payload.get("symbol"))

    bus.on(EventType.RISK_APPROVED, on_approved)
    await bus.start()
    e = Event(EventType.RISK_APPROVED, "bot1", {"symbol": "btcusdt"}, correlation_id="abc123")
    await bus.emit(e)
    await bus.emit(e)  # duplicate — must not double-count
    assert len(fills) == 1, f"expected 1 fill, got {len(fills)}"
    print("idempotency_ok")

asyncio.run(main())
PY

echo "==> pytest subset"
python3 -m pytest tests/test_order_state_machine.py tests/test_idempotency.py \
  tests/test_leakage_guard.py tests/test_portfolio_netting.py tests/test_reconnect_guard.py \
  -q --tb=line

echo "run-pipeline-smoke: PASS"

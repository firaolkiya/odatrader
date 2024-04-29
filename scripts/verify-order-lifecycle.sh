#!/usr/bin/env bash
# Bash-driven order state machine verification (partial fill → fill → cancel rejection).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

export PYTHONPATH="$ROOT"

run_case() {
  local name="$1"
  local script="$2"
  local expected="$3"
  if python3 -c "$script" >/dev/null 2>"$TMP/err"; then
    rc=0
  else
    rc=$?
  fi
  if [[ "$rc" -eq "$expected" ]]; then
    echo "  ok  $name (exit $rc)"
  else
    echo "  FAIL $name (expected exit $expected, got $rc)" >&2
    cat "$TMP/err" >&2
    return 1
  fi
}

echo "==> order lifecycle cases"

run_case "partial-then-fill" "
from backend.orders.manager import OrderManager
from backend.orders.models import Order, OrderSide, OrderStatus
m = OrderManager()
o = Order('btcusdt', OrderSide.BUY, 1.0)
m.submit(o)
m.fill(o.id, 0.4, 100.0)
m.fill(o.id, 0.6, 101.0)
assert m.get(o.id).status == OrderStatus.FILLED
assert abs(m.get(o.id).avg_fill_price - 100.6) < 0.01
" 0

run_case "cancel-open" "
from backend.orders.manager import OrderManager
from backend.orders.models import Order, OrderSide, OrderStatus
m = OrderManager()
o = Order('ethusdt', OrderSide.SELL, 2.0)
m.submit(o)
m.cancel(o.id)
assert m.get(o.id).status == OrderStatus.CANCELLED
" 0

run_case "reject-fill-cancelled" "
from backend.orders.manager import OrderManager
from backend.orders.models import Order, OrderSide
from backend.orders.state_machine import InvalidOrderTransition
m = OrderManager()
o = Order('btcusdt', OrderSide.BUY, 1.0)
m.submit(o)
m.cancel(o.id)
try:
    m.fill(o.id, 0.5, 100.0)
except InvalidOrderTransition:
    raise SystemExit(0)
raise SystemExit(1)
" 0

run_case "reject-overfill" "
from backend.orders.manager import OrderManager
from backend.orders.models import Order, OrderSide
m = OrderManager()
o = Order('btcusdt', OrderSide.BUY, 1.0)
m.submit(o)
try:
    m.fill(o.id, 1.5, 100.0)
except ValueError:
    raise SystemExit(0)
raise SystemExit(1)
" 0

echo "verify-order-lifecycle: PASS"

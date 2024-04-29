#!/usr/bin/env python3
"""OdaTrade command-line interface for platform and bot management."""
import argparse
import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def cmd_status(args):
    try:
        import requests
        base = os.getenv("API_BASE", "http://localhost:8000")
        resp = requests.get(f"{base}/status", timeout=5)
        print(json.dumps(resp.json(), indent=2))
    except Exception:
        from backend.integration.legacy_bridge import get_legacy_bridge
        print(json.dumps(get_legacy_bridge().get_status(), indent=2))


def cmd_start(args):
    if args.legacy:
        from backend.integration.legacy_bridge import get_legacy_bridge
        result = get_legacy_bridge().start_legacy_bot()
        print(f"Legacy bot started: {result}")
        return
    try:
        from backend.bots.manager import BotManager
        from backend.bots.config import BotConfig
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        mgr = BotManager(redis_url=redis_url)
        mgr.start_platform()
        config = BotConfig(
            name=args.name or "CLI Bot",
            symbols=args.symbols.split(",") if args.symbols else ["btcusdt"],
            risk_profile=args.risk or "moderate",
        )
        config = mgr.create_bot(config)
        result = mgr.start_bot(config.bot_id)
        print(f"Bot started: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Start failed: {e}")
        from backend.integration.legacy_bridge import get_legacy_bridge
        result = get_legacy_bridge().start_legacy_bot()
        print(f"Fallback legacy start: {result}")


def cmd_stop(args):
    try:
        from backend.api.routes.bots_api import get_bot_manager
        mgr = get_bot_manager()
        if args.bot_id:
            result = mgr.stop_bot(args.bot_id)
        else:
            mgr.stop_all()
            result = {"status": "all_stopped"}
        print(json.dumps(result, indent=2))
    except Exception:
        from backend.integration.legacy_bridge import get_legacy_bridge
        print(json.dumps(get_legacy_bridge().stop_legacy_bot(), indent=2))


def cmd_backtest(args):
    print(f"Backtest {args.symbol} for {args.days} days (strategy={args.strategy})")
    try:
        import pandas as pd
        from backend.backtesting.engine import BacktestEngine
        from backend.data.historical_loader import load_from_csv
        engine = BacktestEngine(initial_balance=args.balance)
        print("Backtest engine ready. Provide CSV data to run.")
    except Exception as e:
        print(f"Backtest setup error: {e}")


def cmd_platform(args):
    async def run():
        from odatrade.core.startup import run_platform
        await run_platform()
    print("Starting OdaTrade platform...")
    asyncio.run(run())


def cmd_bots(args):
    try:
        import requests
        base = os.getenv("API_BASE", "http://localhost:8000")
        resp = requests.get(f"{base}/bots/", timeout=5)
        print(json.dumps(resp.json(), indent=2))
    except Exception as e:
        print(f"Failed to list bots: {e}")


def main():
    parser = argparse.ArgumentParser(description="OdaTrade CLI — Scalable Trading Platform")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("status", help="Show platform/bot status").set_defaults(func=cmd_status)

    start = sub.add_parser("start", help="Start trading bot")
    start.add_argument("--name", default="CLI Bot")
    start.add_argument("--symbols", default="btcusdt,ethusdt")
    start.add_argument("--risk", choices=["conservative", "moderate", "aggressive"])
    start.add_argument("--legacy", action="store_true", help="Use legacy framework")
    start.set_defaults(func=cmd_start)

    stop = sub.add_parser("stop", help="Stop trading bot")
    stop.add_argument("--bot-id", help="Specific bot to stop")
    stop.set_defaults(func=cmd_stop)

    bt = sub.add_parser("backtest", help="Run backtest")
    bt.add_argument("--symbol", default="btcusdt")
    bt.add_argument("--days", type=int, default=30)
    bt.add_argument("--strategy", default="rsi")
    bt.add_argument("--balance", type=float, default=5000)
    bt.set_defaults(func=cmd_backtest)

    sub.add_parser("platform", help="Start full platform").set_defaults(func=cmd_platform)
    sub.add_parser("bots", help="List all bots").set_defaults(func=cmd_bots)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

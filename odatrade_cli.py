#!/usr/bin/env python3
"""OdaTrade command-line interface."""
import argparse

def main():
    parser = argparse.ArgumentParser(description="OdaTrade CLI")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("status", help="Show bot status")
    sub.add_parser("start", help="Start trading bot")
    sub.add_parser("stop", help="Stop trading bot")
    backtest = sub.add_parser("backtest", help="Run backtest")
    backtest.add_argument("--symbol", default="btcusdt")
    backtest.add_argument("--days", type=int, default=30)

    args = parser.parse_args()
    if args.cmd == "status":
        print("OdaTrade bot: stopped")
    elif args.cmd == "start":
        print("Starting OdaTrade bot...")
    elif args.cmd == "stop":
        print("Stopping OdaTrade bot...")
    elif args.cmd == "backtest":
        print(f"Backtest {args.symbol} for {args.days} days")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

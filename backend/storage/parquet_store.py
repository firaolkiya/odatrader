"""Parquet storage for historical bars and backtest outputs."""
import logging
from pathlib import Path
from typing import Optional
import pandas as pd

logger = logging.getLogger("odatrade.storage")


class ParquetStore:
    def __init__(self, base_dir: str = "data/parquet"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_bars(self, symbol: str, df: pd.DataFrame, timeframe: str = "1m"):
        path = self.base_dir / "bars" / symbol / f"{timeframe}.parquet"
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(path, index=False)
        logger.info("Saved %d bars for %s/%s", len(df), symbol, timeframe)

    def load_bars(self, symbol: str, timeframe: str = "1m") -> Optional[pd.DataFrame]:
        path = self.base_dir / "bars" / symbol / f"{timeframe}.parquet"
        if not path.exists():
            return None
        return pd.read_parquet(path)

    def save_backtest(self, run_id: str, results: dict):
        path = self.base_dir / "backtests" / run_id
        path.mkdir(parents=True, exist_ok=True)
        if "equity" in results:
            pd.DataFrame({"equity": results["equity"]}).to_parquet(path / "equity.parquet")
        if "trade_details" in results:
            pd.DataFrame(results["trade_details"]).to_parquet(path / "trades.parquet")
        logger.info("Saved backtest %s", run_id)

    def list_backtests(self) -> list:
        bt_dir = self.base_dir / "backtests"
        if not bt_dir.exists():
            return []
        return [d.name for d in bt_dir.iterdir() if d.is_dir()]

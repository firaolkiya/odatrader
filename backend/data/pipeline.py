"""ETL data pipeline for OdaTrade."""
from backend.core.feature_engineering import compute_features
import pandas as pd

class DataPipeline:
    def __init__(self, engine):
        self.engine = engine

    def ingest(self, symbol: str, raw_df: pd.DataFrame) -> pd.DataFrame:
        df = raw_df.copy()
        df["symbol"] = symbol
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return compute_features(df)

    def run(self, symbol: str, raw_df: pd.DataFrame) -> pd.DataFrame:
        return self.transform(self.ingest(symbol, raw_df))

"""OdaTrade paper trading mode."""
from backend.execution.execution_engine import ExecutionEngine

class PaperTradingMode:
    def __init__(self, engine: ExecutionEngine):
        self.engine = engine
        self.active = True

    def execute(self, symbol: str, signal: str, price: float):
        if not self.active:
            return None
        return self.engine.execute_trade(symbol, signal, price)

"""OdaTrade exception hierarchy."""

class OdaTradeError(Exception):
    """Base exception for OdaTrade."""

class ConfigError(OdaTradeError):
    pass

class ExchangeError(OdaTradeError):
    pass

class StrategyError(OdaTradeError):
    pass

class RiskLimitError(OdaTradeError):
    pass

class BacktestError(OdaTradeError):
    pass

class AuthError(OdaTradeError):
    pass

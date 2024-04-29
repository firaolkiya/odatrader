"""Global error handling and retry middleware for OdaTrade API."""
import logging
import time
import traceback
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from odatrade.core.exceptions import (
    OdaTradeError, ConfigError, ExchangeError, StrategyError,
    RiskLimitError, BacktestError, AuthError,
)

logger = logging.getLogger("odatrade.api.errors")

EXCEPTION_MAP = {
    ConfigError: (400, "configuration_error"),
    ExchangeError: (502, "exchange_error"),
    StrategyError: (500, "strategy_error"),
    RiskLimitError: (429, "risk_limit_exceeded"),
    BacktestError: (400, "backtest_error"),
    AuthError: (401, "authentication_error"),
    OdaTradeError: (500, "odatrade_error"),
}


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.time()
        try:
            response = await call_next(request)
            elapsed = (time.time() - start) * 1000
            response.headers["X-Response-Time-Ms"] = str(round(elapsed, 2))
            response.headers["X-Service"] = "OdaTrade"
            return response
        except Exception as exc:
            elapsed = (time.time() - start) * 1000
            status_code, error_type = 500, "internal_error"
            for exc_class, (code, etype) in EXCEPTION_MAP.items():
                if isinstance(exc, exc_class):
                    status_code, error_type = code, etype
                    break

            logger.error(
                "Request error: %s %s → %s (%s)",
                request.method, request.url.path, error_type, str(exc),
            )
            return JSONResponse(
                status_code=status_code,
                content={
                    "error": error_type,
                    "message": str(exc),
                    "path": request.url.path,
                    "timestamp": time.time(),
                    "response_time_ms": round(elapsed, 2),
                },
            )


class RetryMiddleware(BaseHTTPMiddleware):
    """Retry failed requests to external services with exponential backoff."""

    def __init__(self, app, max_retries: int = 3, base_delay: float = 0.5):
        super().__init__(app)
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        last_exc = None
        for attempt in range(self.max_retries):
            try:
                return await call_next(request)
            except ConnectionError as e:
                last_exc = e
                delay = self.base_delay * (2 ** attempt)
                logger.warning("Retry %d/%d for %s (delay=%.1fs)", attempt + 1, self.max_retries, request.url.path, delay)
                time.sleep(delay)
            except Exception:
                raise
        raise last_exc

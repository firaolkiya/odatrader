"""SQLAlchemy ORM models for OdaTrade."""
from sqlalchemy import Column, String, Float, DateTime, Boolean, Integer, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class MarketCandle(Base):
    __tablename__ = "market_data"
    symbol = Column(String, primary_key=True)
    timestamp = Column(DateTime(timezone=True), primary_key=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String)
    side = Column(String)
    price = Column(Float)
    quantity = Column(Float)
    pnl = Column(Float, default=0.0)
    timestamp = Column(DateTime(timezone=True))
    strategy = Column(String)

class StrategySignal(Base):
    __tablename__ = "strategy_signals"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String)
    strategy = Column(String)
    action = Column(String)
    timestamp = Column(DateTime(timezone=True))
    executed = Column(Boolean, default=False)
    reason = Column(Text, default="")

class AlertLog(Base):
    __tablename__ = "alert_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel = Column(String)
    message = Column(Text)
    timestamp = Column(DateTime(timezone=True))
    delivered = Column(Boolean, default=False)

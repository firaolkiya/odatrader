import datetime
import httpx
import os
import sys
import pandas as pd
import asyncio
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.db.market_data import get_latest_prices_df

from config.config import GROQ_API_KEY


class GPTStrategy:
    def __init__(self, symbol: str):
        self.symbol = symbol.upper()
        self.name = "GPTStrategy"
        print(f"[GPTStrategy] Initialized for {self.symbol}")

    def generate_prompt(self, symbol: str, open: float, high: float, low: float, 
                   close: float, rsi: float, ema_fast: float, ema_slow: float,
                   macd: float, volume: float, timestamp: str) -> str:
        return f"""
    CRYPTOCURRENCY TRADING DECISION SYSTEM (v2.2 Active)

    You are an AI trading analyst evaluating {symbol} at {timestamp}.

    === MARKET DATA ===
    [Price Action]
    - Open/Close: {open:.4f} → {close:.4f} ({'🟢 Bullish' if close > open else '🔴 Bearish'})
    - Range: {high:.4f} (High) | {low:.4f} (Low)
    - Volume: {volume:.2f} ({'📈 High' if volume > 10000 else '📉 Low'})

    [Technical Indicators]
    - RSI (14): {rsi:.2f} → {self._rsi_strength(rsi)}
    - EMA Cross: {ema_fast:.2f} > {ema_slow:.2f} → {'🟢 Bullish' if ema_fast > ema_slow else '🔴 Bearish'}
    - MACD: {macd:.2f} → {self._macd_strength(macd)}

    === ACTIVE TRADING RULES ===
    🔴 SELL WHEN (REQUIRE 1/3):
    1) RSI > 60 {'✅' if rsi > 60 else '❌'}
    2) EMA Bearish {'✅' if ema_fast < ema_slow else '❌'} 
    3) MACD < -0.2 {'✅' if macd < -0.2 else '❌'}

    🟢 BUY WHEN (REQUIRE 1/3):
    1) RSI < 40 {'✅' if rsi < 40 else '❌'}
    2) EMA Bullish {'✅' if ema_fast > ema_slow else '❌'}
    3) MACD > 0.2 {'✅' if macd > 0.2 else '❌'}

    ⚪ HOLD ONLY WHEN:
    - All indicators are completely neutral
    - No clear trend in price action

    === WEIGHTED DECISION FACTORS ===
    Volume Impact (30% weight):
    - High volume strengthens current trend {'✅' if volume > 10000 else '❌'}

    Price Momentum (40% weight):
    - Recent price direction: {'🟢 Up' if close > open else '🔴 Down'}

    Indicator Alignment (30% weight):
    - Bullish indicators: {sum([1 if rsi < 40 else 0, 1 if ema_fast > ema_slow else 0, 1 if macd > 0.2 else 0])}/3
    - Bearish indicators: {sum([1 if rsi > 60 else 0, 1 if ema_fast < ema_slow else 0, 1 if macd < -0.2 else 0])}/3

    === FINAL DECISION TREE ===
    1) Prefer BUY/SELL when any 1 indicator suggests it
    2) Consider volume and price momentum as tie-breakers
    3) Only HOLD when absolutely no signals present

    OUTPUT ONLY ONE WORD:
    - "SELL" if  🔴 conditions met are more than 🟢
    - "BUY" if  🟢 conditions met  are more than 🔴
    - "HOLD" only if completely neutral
    """

    # Modified helper methods
    def _rsi_strength(self, rsi: float) -> str:
        if rsi > 65: return "🔴 SELL SIGNAL"
        if rsi > 55: return "⚠️ Mild Overbought"
        if rsi < 35: return "🟢 BUY SIGNAL"
        if rsi < 45: return "⚠️ Mild Oversold"
        return "⚖️ Neutral"

    def _macd_strength(self, macd: float) -> str:
        if macd > 0.3: return "🟢 BUY SIGNAL"
        if macd > 0.1: return "🟢 Mild Bullish"
        if macd < -0.3: return "🔴 SELL SIGNAL"
        if macd < -0.1: return "🔴 Mild Bearish"
        return "⚖️ Neutral"
    def evaluate(self, price_override=None, sentiment_override=None, timestamp_override=None):
        try:
            print(f"[GPTStrategy] Fetching data for {self.symbol}...")
            
            # Fetch market data
            if price_override and timestamp_override:
                print("[GPTStrategy] Using price override")
                open, high, low, close, volume = price_override
                timestamp = timestamp_override
            else:
                price_data = get_latest_prices_df(self.symbol)
                if price_data.empty:
                    print("[GPTStrategy] WARNING: No market data available")
                    return {
                        "action": "HOLD", 
                        "strategy": self.name,
                        "reason": "No market data"
                    }

                latest = price_data.iloc[-1]
                open = latest['open']
                high = latest["high"]
                low = latest["low"]
                close = latest["close"]
                volume = latest["volume"]
                timestamp = str(latest['timestamp'])

            # Calculate indicators
            rsi = RSIIndicator(close=price_data['close'], window=14).rsi().iloc[-1]
            ema_fast = EMAIndicator(close=price_data['close'], window=9).ema_indicator().iloc[-1]
            ema_slow = EMAIndicator(close=price_data['close'], window=21).ema_indicator().iloc[-1]
            macd = MACD(close=price_data['close'], window_fast=12, window_slow=26, window_sign=9).macd().iloc[-1]

            # Get sentiment
            
                   

            # Generate and send prompt
            prompt = self.generate_prompt(
                symbol=self.symbol,
                open=open,
                high=high,
                low=low,
                close=close,
                rsi=rsi,
                ema_fast=ema_fast,
                ema_slow=ema_slow,
                macd=macd,
                volume=volume,
                
                timestamp=timestamp
            )

            print("[GPTStrategy] Sending request to Groq API...")
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
            payload = {
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": "You're a crypto trading expert."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,  # Slightly higher for more varied responses
                "max_tokens": 10      # Limit response length
            }

            with httpx.Client(timeout=30.0) as client:
                res = client.post(
                    "https://api.groq.com/openai/v1/chat/completions", 
                    json=payload, 
                    headers=headers
                )
                res.raise_for_status()
                response = res.json()
                raw_decision = response["choices"][0]["message"]["content"].strip().upper()
                print(f"[GPTStrategy] Raw API response: {raw_decision}")

            # Parse decision (more robust)
            decision = "HOLD"
            if "BUY" in raw_decision:
                decision = "BUY"
            elif "SELL" in raw_decision:
                decision = "SELL"

            return {
                "action": decision,
                "strategy": self.name,
                "reason": f"GPT analysis: {raw_decision[:100]}...",
                "details": {
                    "rsi": rsi,
                    "ema_cross": "Bullish" if ema_fast > ema_slow else "Bearish",
                    "macd": macd
                    
                }
            }

        except httpx.HTTPError as e:
            print(f"[GPTStrategy] API Error: {str(e)}")
            return {
                "action": "HOLD",
                "strategy": self.name,
                "reason": f"API Error: {str(e)}"
            }
        except Exception as e:
            print(f"[GPTStrategy] Unexpected Error: {str(e)}")
            return {
                "action": "HOLD",
                "strategy": self.name,
                "reason": f"Error: {str(e)}"
            }


if __name__ == "__main__":
    print("\n=== Testing GPTStrategy ===")
    strategy = GPTStrategy("SOLUSDT")
    result = strategy.evaluate()
    print("\nFinal Result:")
    print(result)


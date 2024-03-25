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
from backend.sentiments.reddit_scraper import get_reddit_sentiment_sync_safe
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
    CRYPTOCURRENCY TRADING DECISION SYSTEM (v2.1 Balanced)

    You are an impartial AI trading analyst evaluating {symbol} at {timestamp}.

    === MARKET DATA ===
    [Price Action]
    - Open/Close: {open:.4f} → {close:.4f} ({'🟢 Bullish' if close > open else '🔴 Bearish'})
    - Range: {high:.4f} (High) | {low:.4f} (Low)
    - Volume: {volume:.2f} ({'📈 High' if volume > 10000 else '📉 Low'})

    [Technical Indicators]
    - RSI (14): {rsi:.2f} → {self._rsi_strength(rsi)}
    - EMA Cross: {ema_fast:.2f} > {ema_slow:.2f} → {'🟢 Bullish' if ema_fast > ema_slow else '🔴 Bearish'}
    - MACD: {macd:.2f} → {self._macd_strength(macd)}

    === BALANCED TRADING RULES ===
    🔴 STRONG SELL WHEN (REQUIRE 2/3):
    1) RSI > 65 {'✅' if rsi > 65 else '❌'}
    2) EMA Bearish {'✅' if ema_fast < ema_slow else '❌'} 
    3) MACD < -0.3 {'✅' if macd < -0.3 else '❌'}

    🟢 STRONG BUY WHEN (REQUIRE 2/3):
    1) RSI < 35 {'✅' if rsi < 35 else '❌'}
    2) EMA Bullish {'✅' if ema_fast > ema_slow else '❌'}
    3) MACD > 0.3 {'✅' if macd > 0.3 else '❌'}

    ⚪ HOLD WHEN:
    - Mixed signals (1 buy + 1 sell condition)
    - RSI between 40-60
    - MACD between -0.2 and 0.2
    - No clear trend confirmation

    === CONFIRMATION FACTORS ===
    Volume Confirmation:
    - Bullish: Rising volume on up moves {'✅' if volume > 10000 and close > open else '❌'}
    - Bearish: Rising volume on down moves {'✅' if volume > 10000 and close < open else '❌'}

    Price Patterns:
    - Higher highs/lows → Strengthens BUY
    - Lower highs/lows → Strengthens SELL

    === RISK MANAGEMENT ===
    ⚠️ NEVER BUY WHEN:
    - RSI > 60 + Bearish EMA cross
    - Volume declining during upticks

    ⚠️ NEVER SELL WHEN:
    - RSI < 40 + Bullish EMA cross
    - MACD histogram rising

    === FINAL DECISION TREE ===
    1) Check if SELL conditions met (2/3)
    2) If not, check if BUY conditions met (2/3) 
    3) Default to HOLD for uncertainty

    OUTPUT ONLY ONE WORD:
    - "SELL" if 🔴 conditions met
    - "BUY" if 🟢 conditions met  
    - "HOLD" if ⚪ neutral/mixed
    """

    # Enhanced helper methods
    def _rsi_strength(self, rsi: float) -> str:
        if rsi > 70: return "🔥 EXTREME OVERBOUGHT (STRONG SELL)"
        if rsi > 60: return "⚠️ Overbought (Potential Sell)"
        if rsi < 30: return "🔥 EXTREME OVERSOLD (STRONG BUY)"
        if rsi < 40: return "⚠️ Oversold (Potential Buy)"
        return "⚖️ Neutral (Hold)"

    def _macd_strength(self, macd: float) -> str:
        if macd > 0.5: return "🚀 STRONG BULLISH"
        if macd > 0.2: return "🟢 Bullish"
        if macd < -0.5: return "💣 STRONG BEARISH"
        if macd < -0.2: return "🔴 Bearish"
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


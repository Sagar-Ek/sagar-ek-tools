import logging
from datetime import datetime, timezone
from typing import Any, Dict
import ccxt.async_support as ccxt

logger = logging.getLogger("services.market_data")


async def fetch_btcusdt_market_data(symbol: str = "BTC/USDT") -> Dict[str, Any]:
    """
    Fetch real-time ticker and order book data from Binance via CCXT.
    """
    exchange = ccxt.binance({"enableRateLimit": True})
    try:
        ticker = await exchange.fetch_ticker(symbol)
        order_book = await exchange.fetch_order_book(symbol, limit=5)
        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        data = {
            "symbol": symbol,
            "timestamp_utc": now_utc,
            "price": ticker.get("last"),
            "high_24h": ticker.get("high"),
            "low_24h": ticker.get("low"),
            "percentage_24h": ticker.get("percentage"),
            "volume_24h": ticker.get("baseVolume"),
            "bids_top": order_book.get("bids", [])[:3],
            "asks_top": order_book.get("asks", [])[:3],
        }
        return data
    except Exception as exc:
        logger.error("CCXT market data fetch error (%s): %s", symbol, exc)
        raise
    finally:
        await exchange.close()


async def get_market_summary_text(symbol: str = "BTC/USDT") -> str:
    """
    Generate formatted market data summary string in English for AI prompt.
    """
    try:
        data = await fetch_btcusdt_market_data(symbol)
        summary = (
            f"[{data['symbol']} Real-time Market Data (Binance)]\n"
            f"- Timestamp: {data['timestamp_utc']}\n"
            f"- Current Price: ${data['price']:,.2f}\n"
            f"- 24h Change: {data['percentage_24h']}%\n"
            f"- 24h High / Low: ${data['high_24h']:,.2f} / ${data['low_24h']:,.2f}\n"
            f"- 24h Volume: {data['volume_24h']:,.2f} BTC\n"
            f"- Top Bids: {data['bids_top']}\n"
            f"- Top Asks: {data['asks_top']}"
        )
        return summary
    except Exception as exc:
        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        logger.warning("Failed to fetch market data, using fallback: %s", exc)
        return f"[{symbol} Real-time Market Data]\nTimestamp: {now_utc} (Data fetch temporarily unavailable)"

from unittest.mock import AsyncMock, patch
import pytest
from app.services.market_data import fetch_btcusdt_market_data, get_market_summary_text


@pytest.mark.anyio
async def test_fetch_btcusdt_market_data() -> None:
    mock_exchange = AsyncMock()
    mock_exchange.fetch_ticker.return_value = {
        "last": 75000.0,
        "high": 76000.0,
        "low": 74000.0,
        "percentage": 1.5,
        "baseVolume": 1000.0,
    }
    mock_exchange.fetch_order_book.return_value = {
        "bids": [[74990.0, 1.0]],
        "asks": [[75010.0, 1.5]],
    }
    mock_exchange.close = AsyncMock()

    with patch("ccxt.async_support.binance", return_value=mock_exchange):
        data = await fetch_btcusdt_market_data("BTC/USDT")
        assert data["price"] == 75000.0
        assert data["high_24h"] == 76000.0
        assert data["percentage_24h"] == 1.5
        assert len(data["bids_top"]) == 1


@pytest.mark.anyio
async def test_get_market_summary_text() -> None:
    fake_data = {
        "symbol": "BTC/USDT",
        "timestamp_utc": "2026-11-08 00:00:00 UTC",
        "price": 75000.0,
        "percentage_24h": 1.5,
        "high_24h": 76000.0,
        "low_24h": 74000.0,
        "volume_24h": 1000.0,
        "bids_top": [[74990.0, 1.0]],
        "asks_top": [[75010.0, 1.5]],
    }

    with patch("app.services.market_data.fetch_btcusdt_market_data", AsyncMock(return_value=fake_data)):
        summary = await get_market_summary_text("BTC/USDT")
        assert "75,000.00" in summary
        assert "BTC/USDT" in summary

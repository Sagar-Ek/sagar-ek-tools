import json
import logging
import os
import re
from datetime import datetime
from typing import Optional
import litellm
from litellm import acompletion
from app.services.market_data import get_market_summary_text

logger = logging.getLogger("jobs.ai_query")

litellm.suppress_debug_info = True

SYSTEM_PROMPT = "You are an algorithmic trader specializing in short-term cryptocurrency (BTCUSDT) trading."

DEFAULT_MODEL = "gemini/gemini-3.1-flash-lite"

PRICE_FIELDS = [
    "price",
    "longEntryPrice",
    "shortEntryPrice",
    "longStopLossPrice",
    "shortStopLossPrice",
    "longTakeProfitPrice",
    "shortTakeProfitPrice",
]


def format_prices_to_2_decimals(response_text: str) -> str:
    """
    Parse JSON from AI response and guarantee all price fields are formatted
    to exactly 2 decimal places (e.g. 75100.00).
    """
    cleaned = re.sub(r"^```json\s*", "", response_text.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"```$", "", cleaned.strip())
    try:
        data = json.loads(cleaned)
    except Exception:
        return response_text

    for key in PRICE_FIELDS:
        val = data.get(key)
        if val not in (None, ""):
            try:
                num_str = str(val).replace(",", "").replace("$", "").strip()
                data[key] = f"{float(num_str):.2f}"
            except (ValueError, TypeError):
                pass

    return json.dumps(data, ensure_ascii=False, indent=2)


async def get_prompt() -> str:
    market_data = await get_market_summary_text("BTC/USDT")
    return f"""Analyze the following real-time market data and determine the recommended actions for ultra-short-term trading (scalping / day trading over the next several minutes to tens of minutes).

{market_data}

The output must be exclusively in the following JSON format (Markdown code block, i.e., ```json ... ```, is acceptable). Do not include any other greetings or conversational text:
{{
  \"datetime\": \"Current UTC datetime (YYYY-MM-DD HH:MM:SS UTC)\",
  \"direction\": \"\"Up\" or \"Down\" (expected market direction over the next several minutes to tens of minutes)\",
  \"price\": \"Current USDT price (2 decimal places, e.g., 75850.50)\",
  \"entry\": \"\"Buy\" or \"Sell\" to open an immediate market position; otherwise, \"\"\",
  \"longPosition\": \"\"Hold\" if current market conditions favor holding/maintaining a long position; otherwise, \"\"\",
  \"longPositionReason\": \"Brief explanation in Japanese of the rationale for holding or not holding/avoiding a long position\",
  \"shortPosition\": \"\"Hold\" if current market conditions favor holding/maintaining a short position; otherwise, \"\"\",
  \"shortPositionReason\": \"Brief explanation in Japanese of the rationale for holding or not holding/avoiding a short position\",
  \"longEntryPrice\": \"Recommended limit entry price for long (mandatory: 2 decimal places, e.g., 75570.00)\",
  \"shortEntryPrice\": \"Recommended limit entry price for short (mandatory: 2 decimal places, e.g., 76250.00)\",
  \"longStopLossPrice\": \"Recommended stop-loss price for long (mandatory: 2 decimal places, e.g., 75100.00)\",
  \"shortStopLossPrice\": \"Recommended stop-loss price for short (mandatory: 2 decimal places, e.g., 76600.00)\",
  \"longTakeProfitPrice\": \"Recommended take-profit price for long (mandatory: 2 decimal places, e.g., 76300.00)\",
  \"shortTakeProfitPrice\": \"Recommended take-profit price for short (mandatory: 2 decimal places, e.g., 75300.00)\",
  \"reason\": \"Brief explanation of the rationale for your decision in Japanese\"
}}

*Critical Rules:
- direction must be strictly either \"Up\" or \"Down\".
- Signal consistency:
  - If entry == \"Buy\", shortPosition must NOT be \"Hold\" (buying and holding short are contradictory).
  - If entry == \"Sell\", longPosition must NOT be \"Hold\" (selling and holding long are contradictory).
  - If entry == \"Buy\", longPosition should typically be \"Hold\".
  - If entry == \"Sell\", shortPosition should typically be \"Hold\".
  - If entry == \"Buy\", longEntryPrice should reflect the immediate execution price (~price).
  - If entry == \"Sell\", shortEntryPrice should reflect the immediate execution price (~price).
- Price hierarchy constraints must be strictly adhered to:
  - Long: longTakeProfitPrice > longEntryPrice > longStopLossPrice
  - Short: shortStopLossPrice > shortEntryPrice > shortTakeProfitPrice
  - Limit entry placement: longEntryPrice <= price (buy pullbacks) and shortEntryPrice >= price (sell rallies) unless an immediate market entry is triggered.
- All price fields (price, longEntryPrice, shortEntryPrice, longStopLossPrice, shortStopLossPrice, longTakeProfitPrice, shortTakeProfitPrice) must be formatted to exactly 2 decimal places (e.g., 75850.50, 75570.00), even if ending in .00.
- Even if entry is empty (no immediate trade), all price fields are mandatory and must never be empty strings. Provide explicit reference levels based on key support and resistance zones.
""".strip()


def normalize_model_name(model: str) -> str:
    if model.startswith("gemini") and "/" not in model:
        return f"gemini/{model}"
    return model


async def query_ai(prompt: Optional[str] = None) -> str:
    target_prompt = prompt or await get_prompt()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        mock_data = {
            "datetime": "2026-11-08 00:00:00 UTC",
            "direction": "Up",
            "price": "75000.00",
            "entry": "",
            "longPosition": "Hold",
            "longPositionReason": "サポートライン維持のためロング保有推奨",
            "shortPosition": "",
            "shortPositionReason": "上昇モメンタムが強くショート保有はリスク過大",
            "longEntryPrice": "74500.00",
            "shortEntryPrice": "75500.00",
            "longStopLossPrice": "74000.00",
            "shortStopLossPrice": "76000.00",
            "longTakeProfitPrice": "75800.00",
            "shortTakeProfitPrice": "74200.00",
            "reason": "モック実行",
        }
        mock_response = f"[MOCK AI] ({timestamp}) AI_API_KEY is not set. Simulation execution:\n{json.dumps(mock_data, ensure_ascii=False, indent=2)}"
        logger.info(mock_response)
        return mock_response

    raw_model = os.getenv("AI_MODEL", DEFAULT_MODEL)
    model = normalize_model_name(raw_model)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": target_prompt},
    ]

    try:
        response = await acompletion(
            model=model,
            messages=messages,
            api_key=api_key,
            temperature=0.3,
            max_tokens=500,
        )
        raw_message = response.choices[0].message.content.strip()
        formatted_message = format_prices_to_2_decimals(raw_message)
        logger.info("AI response received (%s):\n%s", timestamp, formatted_message)
        return formatted_message
    except Exception as exc:
        logger.error("Error occurred during LiteLLM query: %s", exc)
        raise


async def query_ai_job() -> None:
    logger.info("Starting minutely AI trading analysis job")
    try:
        await query_ai()
    except Exception as exc:
        logger.warning("AI trading analysis job completed with error: %s", exc)

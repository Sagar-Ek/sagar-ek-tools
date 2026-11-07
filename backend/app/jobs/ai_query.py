import logging
from datetime import datetime
from typing import Optional
import httpx
from app.core.config import settings

logger = logging.getLogger("jobs.ai_query")


async def query_ai(prompt: Optional[str] = None) -> str:
    """
    AI API（OpenAI互換APIなど）に問い合わせを行う非同期関数。
    AI_API_KEY が未設定の場合はログ出力の上モック応答を返します。
    """
    target_prompt = prompt or settings.AI_PROMPT
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not settings.AI_API_KEY:
        mock_response = (
            f"[MOCK AI] ({timestamp}) AI_API_KEYが未設定のためシミュレーション実行しました: "
            f"システムは正常に稼働しています。"
        )
        logger.info(mock_response)
        return mock_response

    headers = {
        "Authorization": f"Bearer {settings.AI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.AI_MODEL,
        "messages": [
            {"role": "system", "content": "You are a concise system assistant."},
            {"role": "user", "content": target_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 150,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.AI_API_URL,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            message = data["choices"][0]["message"]["content"].strip()
            logger.info("AI 応答を受信しました (%s): %s", timestamp, message)
            return message
    except httpx.HTTPStatusError as exc:
        logger.error(
            "AI API HTTPエラー (ステータス %s): %s",
            exc.response.status_code,
            exc.response.text,
        )
        raise
    except httpx.RequestError as exc:
        logger.error("AI API 接続エラー: %s", exc)
        raise
    except Exception as exc:
        logger.error("AI 問い合わせ中に予期せぬエラーが発生しました: %s", exc)
        raise


async def query_ai_job() -> None:
    """
    APScheduler から毎分0秒に呼び出されるジョブ用エントリポイント。
    例外が発生してもスケジューラ全体がクラッシュしないように保護します。
    """
    logger.info("毎分0秒のAI問い合わせジョブを開始します")
    try:
        await query_ai()
    except Exception as exc:
        logger.warning("AI問い合わせジョブがエラーで終了しました: %s", exc)

import logging
import os
from datetime import datetime
from typing import Optional
import litellm
from litellm import acompletion

logger = logging.getLogger("jobs.ai_query")

# 不要なデバッグ出力を抑制
litellm.suppress_debug_info = True

# ==============================================================================
# AIプロンプト設定（ここを直接編集してプロンプトを変更できます）
# ==============================================================================
SYSTEM_PROMPT = "You are an algorithmic trader specializing in short-term cryptocurrency (BTCUSDT) trading."
DEFAULT_PROMPT = """
Analyze the current BTCUSDT liquidation heatmap and determine the recommended course of action.
Provide your output exclusively in the following JSON format (you may use a Markdown code block, i.e., ```json ... ```, but do not include any additional commentary or greetings).
{"entry": "", "long": "", "short": "", "reason": ""}
*Rules for each field:
entry: "Buy" or "Sell" if initiating a new position; otherwise, ""
long: "Close" if closing an existing long position; otherwise, ""
short: "Close" if closing an existing short position; otherwise, ""
reason: Provide the rationale for your decision in Japanese.
""".strip()

# デフォルトモデル（環境変数 AI_MODEL で上書き可能）
DEFAULT_MODEL = "gemini/gemini-3.1-flash-lite"
# ==============================================================================


def normalize_model_name(model: str) -> str:
    """LiteLLM 用にモデル名を整形（gemini-* でプレフィックス未指定の場合は gemini/ を付与）"""
    if model.startswith("gemini") and "/" not in model:
        return f"gemini/{model}"
    return model


async def query_ai(prompt: Optional[str] = None) -> str:
    """
    LiteLLM を利用して AI（Gemini, OpenAI, Anthropic 等）に問い合わせを行う非同期関数。
    .env の AI_API_KEY が未設定の場合はログ出力の上モック応答を返します。
    """
    target_prompt = prompt or DEFAULT_PROMPT
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # .env から直接取得（config.py を介さない方式）
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        mock_response = (
            f"[MOCK AI] ({timestamp}) AI_API_KEYが未設定のためシミュレーション実行しました: "
            f"システムは正常に稼働しています。"
        )
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
            temperature=0.7,
            max_tokens=150,
        )
        message = response.choices[0].message.content.strip()
        logger.info("AI 応答を受信しました (%s): %s", timestamp, message)
        return message
    except Exception as exc:
        logger.error("LiteLLM 問い合わせ中にエラーが発生しました: %s", exc)
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

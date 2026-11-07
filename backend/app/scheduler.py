import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from app.jobs.ai_query import query_ai_job

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("scheduler")

# ---------------------------------------------------------------------------
# FastAPI (非同期イベントループ) 向けの設定
# ---------------------------------------------------------------------------
async_scheduler = AsyncIOScheduler()

# AI問い合わせタスク
async_scheduler.add_job(
    query_ai_job,
    trigger=CronTrigger(second=0),
    id="ai_query_job",
    name="毎分0秒AI問い合わせタスク",
    replace_existing=True,
)


def start_scheduler() -> None:
    """FastAPI の lifespan 起動時などに呼び出す関数"""
    if not async_scheduler.running:
        async_scheduler.start()
        logger.info("AsyncIOScheduler を開始しました（毎分0秒にAI問い合わせ・定期タスクを実行）")


def shutdown_scheduler() -> None:
    """FastAPI の lifespan 終了時などに呼び出す関数"""
    if async_scheduler.running:
        async_scheduler.shutdown(wait=False)
        logger.info("AsyncIOScheduler を停止しました")


# ---------------------------------------------------------------------------
# 単体スクリプト実行時 (python -m app.scheduler) のブロッキング実行
# ---------------------------------------------------------------------------
def run_standalone() -> None:
    """単体プロセスとして常駐起動する場合の実行関数"""
    blocking_scheduler = BlockingScheduler()
    blocking_scheduler.add_job(
        minutely_task,
        trigger=CronTrigger(second=0),
        id="minutely_task",
        name="毎分0秒定期実行タスク",
        replace_existing=True,
    )
    blocking_scheduler.add_job(
        lambda: asyncio.run(query_ai_job()),
        trigger=CronTrigger(second=0),
        id="ai_query_job",
        name="毎分0秒AI問い合わせタスク",
        replace_existing=True,
    )
    logger.info("BlockingScheduler を開始します（毎分0秒に実行）。停止するには Ctrl+C を押してください。")
    try:
        blocking_scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("スケジューラを停止しました。")


if __name__ == "__main__":
    run_standalone()

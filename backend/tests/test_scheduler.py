import asyncio
import pytest
from app.scheduler import async_scheduler, minutely_task, shutdown_scheduler, start_scheduler


def test_minutely_task_execution() -> None:
    minutely_task()


def test_scheduler_jobs_registered() -> None:
    # 毎分0秒の基本タスク
    min_job = async_scheduler.get_job("minutely_task")
    assert min_job is not None
    assert str(min_job.trigger.fields[7]) == "0"

    # 毎分0秒のAI問い合わせタスク
    ai_job = async_scheduler.get_job("ai_query_job")
    assert ai_job is not None
    assert str(ai_job.trigger.fields[7]) == "0"


@pytest.mark.anyio
async def test_start_and_shutdown_scheduler() -> None:
    start_scheduler()
    assert async_scheduler.running is True
    shutdown_scheduler()
    await asyncio.sleep(0.01)
    assert async_scheduler.running is False

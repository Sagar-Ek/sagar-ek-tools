import asyncio
import pytest
from app.scheduler import async_scheduler, shutdown_scheduler, start_scheduler


def test_scheduler_jobs_registered() -> None:
    ai_job = async_scheduler.get_job("ai_query_job")
    assert ai_job is not None
    # CronTrigger の second が 0 に設定されていることを検証
    assert str(ai_job.trigger.fields[7]) == "0"


@pytest.mark.anyio
async def test_start_and_shutdown_scheduler() -> None:
    start_scheduler()
    assert async_scheduler.running is True
    shutdown_scheduler()
    await asyncio.sleep(0.01)
    assert async_scheduler.running is False

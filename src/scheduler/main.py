import subprocess
import sys

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from src.common.config import get_settings
from src.common.logging import configure_logging, get_logger

logger = get_logger(__name__)
settings = get_settings()


def run_job(module: str) -> None:
    logger.info("Job started", extra={"module": module})
    result = subprocess.run([sys.executable, "-m", module], check=False)  # noqa: S603
    if result.returncode != 0:
        logger.error("Job failed", extra={"module": module, "returncode": result.returncode})
    else:
        logger.info("Job finished", extra={"module": module})


def create_scheduler() -> BlockingScheduler:
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(
        lambda: run_job("src.etl.run_etl"),
        IntervalTrigger(hours=1),
        id="incremental_etl",
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        lambda: run_job("src.crawler.run_crawler"),
        CronTrigger(hour="1", minute="0"),
        id="daily_crawl",
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        lambda: run_job("src.quality.run_quality"),
        CronTrigger(hour="2", minute="30"),
        id="quality_report",
        max_instances=1,
        coalesce=True,
    )
    return scheduler


if __name__ == "__main__":
    configure_logging(settings.log_level)
    create_scheduler().start()

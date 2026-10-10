import os

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from src.common.config import get_settings
from src.common.logging import configure_logging
from src.crawler.spider import ProductSpider


def run() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "src.crawler.settings")
    crawler_settings = get_project_settings()
    crawler_settings.set("MYSQL_URL", settings.mysql_url)
    crawler_settings.set("REDIS_URL", settings.redis_url)
    crawler_settings.set("PLAYWRIGHT_ENABLED", settings.playwright_enabled)
    if settings.playwright_enabled:
        crawler_settings.set(
            "DOWNLOAD_HANDLERS",
            {
                "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
                "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            },
        )
        crawler_settings.set("PLAYWRIGHT_BROWSER_TYPE", settings.playwright_browser)
        crawler_settings.set("PLAYWRIGHT_LAUNCH_OPTIONS", {"headless": True})
    process = CrawlerProcess(crawler_settings)
    process.crawl(
        ProductSpider,
        start_url=settings.start_url,
        playwright_enabled=settings.playwright_enabled,
    )
    process.start()


if __name__ == "__main__":
    run()

from src.common.config import get_settings

settings = get_settings()

BOT_NAME = "ecommerce_price_monitor"
SPIDER_MODULES = ["src.crawler"]
NEWSPIDER_MODULE = "src.crawler"
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = settings.download_delay
CONCURRENT_REQUESTS = settings.concurrent_requests
CONCURRENT_REQUESTS_PER_DOMAIN = settings.concurrent_requests
DOWNLOAD_TIMEOUT = 30
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [408, 429, 500, 502, 503, 504]
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2.0
AUTOTHROTTLE_MAX_DELAY = 30.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
HTTPCACHE_ENABLED = False
JOBDIR = "jobs/crawler"
ITEM_PIPELINES = {
    "src.crawler.pipelines.RedisDeduplicationPipeline": 300,
    "src.crawler.pipelines.RawMySQLPipeline": 400,
}
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
LOG_LEVEL = settings.log_level

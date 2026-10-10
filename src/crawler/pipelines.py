import json

import redis
from scrapy.exceptions import DropItem
from sqlalchemy import text

from src.common.db import create_db_engine, create_session_factory
from src.common.logging import get_logger

logger = get_logger(__name__)


class RedisDeduplicationPipeline:
    def open_spider(self, spider):
        self.redis = redis.Redis.from_url(spider.settings.get("REDIS_URL", "redis://localhost:6379/0"))

    def process_item(self, item, spider):
        key = f"crawler:seen:{spider.name}:{item['source']}:{item['external_id']}:{item['crawl_fingerprint']}"
        if not self.redis.set(key, "1", nx=True, ex=86400):
            raise DropItem(f"duplicate fingerprint: {key}")
        return item


class RawMySQLPipeline:
    def open_spider(self, spider):
        self.engine = create_db_engine(spider.settings.get("MYSQL_URL"))
        self.session_factory = create_session_factory(self.engine)

    def close_spider(self, spider):
        self.engine.dispose()

    def process_item(self, item, spider):
        query = text(
            """
            INSERT INTO raw.raw_product_item
              (source, external_id, url, name, category_name, price, currency, availability,
               rating, raw_payload, crawl_fingerprint, batch_id)
            VALUES
              (:source, :external_id, :url, :name, :category_name, :price, :currency, :availability,
               :rating, CAST(:raw_payload AS JSON), :crawl_fingerprint, :batch_id)
            """
        )
        with self.session_factory() as session:
            session.execute(
                query,
                {**dict(item), "raw_payload": json.dumps(item.get("raw_payload", {}), ensure_ascii=False)},
            )
            session.commit()
        logger.info("raw item stored", extra={"source": item["source"], "external_id": item["external_id"]})
        return item

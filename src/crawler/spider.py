import hashlib
import re
import uuid
from datetime import UTC, datetime
from urllib.parse import urljoin, urlsplit

import scrapy


class ProductSpider(scrapy.Spider):
    name = "public_product_prices"

    def __init__(
        self,
        start_url: str = "https://books.toscrape.com/",
        playwright_enabled: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.start_urls = [start_url]
        self.allowed_domains = [self.extract_domain(start_url)]
        self.batch_id = datetime.now(UTC).strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:8]
        self.playwright_enabled = playwright_enabled

    @staticmethod
    def extract_domain(url: str) -> str:
        return url.split("//", 1)[1].split("/", 1)[0]

    @staticmethod
    def extract_external_id(url: str) -> str:
        path = urlsplit(url).path.rstrip("/")
        segments = path.split("/")
        value = segments[-1]
        if value in {"index", "index.html"} and len(segments) > 1:
            value = segments[-2]
        value = value.split(".", 1)[0]
        return re.sub(r"[^a-zA-Z0-9_-]", "", value)

    def parse(self, response):
        category_name = response.css("h1::text").get(default="").strip()
        for product in response.css("article.product_pod"):
            href = product.css("h3 a::attr(href)").get()
            if href:
                yield response.follow(
                    urljoin(response.url, href),
                    callback=self.parse_product,
                    meta={"category_name": category_name, "playwright": self.playwright_enabled},
                )
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(
                next_page,
                callback=self.parse,
                meta={"playwright": self.playwright_enabled},
            )

    def parse_product(self, response):
        name = response.css("div.product_main h1::text").get(default="").strip()
        price_text = response.css("p.price_color::text").get(default="")
        availability_text = response.css("p.availability::text").get(default="").strip()
        rating_class = response.css("p.star-rating::attr(class)").get(default="")
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        rating = next((score for word, score in rating_map.items() if word in rating_class), None)
        price = round(float(re.sub(r"[^0-9.]", "", price_text)), 2) if re.search(r"\d", price_text) else None
        identity = [name, str(price), availability_text, str(rating)]
        return {
            "source": self.extract_domain(response.url),
            "external_id": self.extract_external_id(response.url),
            "url": response.url,
            "name": name,
            "category_name": response.meta.get("category_name", ""),
            "price": price,
            "currency": "GBP" if "£" in price_text else "",
            "availability": "in_stock" if "In stock" in availability_text else "out_of_stock",
            "rating": rating,
            "raw_payload": {
                "title": name,
                "price_text": price_text,
                "availability_text": availability_text,
                "rating_class": rating_class,
            },
            "crawl_fingerprint": hashlib.sha256("|".join(identity).encode()).hexdigest(),
            "batch_id": self.batch_id,
        }

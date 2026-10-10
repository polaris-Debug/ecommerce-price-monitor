from scrapy import Field, Item


class ProductItem(Item):
    source = Field()
    external_id = Field()
    url = Field()
    name = Field()
    category_name = Field()
    price = Field()
    currency = Field()
    availability = Field()
    rating = Field()
    raw_payload = Field()
    crawl_fingerprint = Field()
    batch_id = Field()

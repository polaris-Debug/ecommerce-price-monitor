from src.crawler.spider import ProductSpider


def test_domain_extraction():
    assert ProductSpider.extract_domain("https://books.toscrape.com/index.html") == "books.toscrape.com"


def test_external_id_extraction():
    url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    assert ProductSpider.extract_external_id(url) == "a-light-in-the-attic_1000"

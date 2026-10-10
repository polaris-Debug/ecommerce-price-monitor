from dataclasses import dataclass


@dataclass(frozen=True)
class Expectation:
    name: str
    query: str
    expectation: str
    severity: str


EXPECTATIONS = [
    Expectation("raw_rows_present", "SELECT COUNT(*) FROM raw.raw_product_item", "value > 0", "critical"),
    Expectation(
        "raw_identity_not_null",
        "SELECT COUNT(*) FROM raw.raw_product_item WHERE source IS NULL OR external_id IS NULL",
        "value = 0",
        "critical",
    ),
    Expectation(
        "ods_complete",
        "SELECT (SELECT COUNT(*) FROM raw.raw_product_item) "
        "- (SELECT COUNT(*) FROM ods.ods_product_snapshot)",
        "value = 0",
        "critical",
    ),
    Expectation(
        "fact_price_not_null",
        "SELECT COUNT(*) FROM dwd.fact_price_snapshot WHERE price IS NULL",
        "value = 0",
        "critical",
    ),
    Expectation(
        "orphan_facts",
        "SELECT COUNT(*) FROM dwd.fact_price_snapshot f "
        "LEFT JOIN dim.dim_product p ON p.product_key=f.product_key "
        "WHERE p.product_key IS NULL",
        "value = 0",
        "critical",
    ),
    Expectation(
        "dimension_categories_present",
        "SELECT COUNT(*) FROM dim.dim_category",
        "value > 0",
        "warning",
    ),
]

from datetime import UTC, datetime
from typing import Annotated, Any, cast

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import CursorResult, text

from src.common.config import get_settings
from src.common.db import check_database, create_db_engine, create_session_factory, session_scope
from src.common.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)
app = FastAPI(
    title="E-commerce Price Monitor API",
    version="1.0.0",
    description="Competitor price monitoring and analysis APIs",
)


def require_service_token(authorization: Annotated[str | None, Header()] = None) -> None:
    if not authorization or authorization != f"Bearer {settings.api_token}":
        raise HTTPException(status_code=401, detail="Invalid service token")


@app.get("/health")
def health() -> dict:
    engine = create_db_engine(settings.mysql_url)
    try:
        return {"status": "ok", "dependencies": check_database(engine)}
    finally:
        engine.dispose()


class ProductCapture(BaseModel):
    source: str
    external_id: str
    url: str
    name: str
    category_name: str
    price: float
    currency: str = "GBP"
    availability: str = "in_stock"
    rating: int | None = None


@app.post("/captures", dependencies=[Depends(require_service_token)])
def ingest_capture(capture: ProductCapture) -> dict:
    engine = create_db_engine(settings.mysql_url)
    session_factory = create_session_factory(engine)
    try:
        with session_scope(session_factory) as session:
            result = session.execute(
                text(
                    """
                    INSERT INTO raw.raw_product_item
                      (source, external_id, url, name, category_name, price, currency, availability,
                       rating, raw_payload, crawl_fingerprint, batch_id, captured_at)
                    VALUES (:source, :external_id, :url, :name, :category_name, :price, :currency,
                            :availability,
                            :rating, JSON_OBJECT('mode','api'),
                            MD5(CONCAT_WS('|', :name, :price, :availability)), :batch_id, UTC_TIMESTAMP())
                    """
                ),
                {
                    "batch_id": f"api-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
                    **capture.model_dump(),
                },
            )
            return {"status": "accepted", "raw_id": cast(CursorResult[Any], result).lastrowid}
    finally:
        engine.dispose()


@app.get("/products/{external_id}/prices", dependencies=[Depends(require_service_token)])
def price_history(
    external_id: str,
    source: str,
    days: Annotated[int, Query(ge=1, le=365)] = 30,
) -> dict:
    engine = create_db_engine(settings.mysql_url)
    session_factory = create_session_factory(engine)
    try:
        with session_scope(session_factory) as session:
            rows = (
                session.execute(
                    text(
                        """
                    SELECT d.calendar_date, p.product_name, s.price, s.availability
                    FROM dwd.fact_price_snapshot s
                    JOIN dim.dim_date d ON d.date_key=s.snapshot_date_key
                    JOIN dim.dim_product p ON p.product_key=s.product_key
                    WHERE p.external_id=:external_id AND s.source=:source
                      AND d.calendar_date >= DATE_SUB(CURRENT_DATE, INTERVAL :days DAY)
                    ORDER BY d.calendar_date
                    """
                    ),
                    {"external_id": external_id, "source": source, "days": days},
                )
                .mappings()
                .all()
            )
            return {"items": [dict(row) for row in rows]}
    finally:
        engine.dispose()

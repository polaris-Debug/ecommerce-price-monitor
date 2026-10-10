from typing import Any, cast

from sqlalchemy import CursorResult, text

from src.common.config import get_settings
from src.common.db import create_db_engine, create_session_factory, session_scope
from src.common.logging import configure_logging, get_logger
from src.etl.sql_transforms import ETL_STATEMENTS

logger = get_logger(__name__)


def run_etl() -> int:
    settings = get_settings()
    configure_logging(settings.log_level)
    engine = create_db_engine(settings.mysql_url)
    session_factory = create_session_factory(engine)
    affected_rows = 0
    try:
        with session_scope(session_factory) as session:
            for statement in ETL_STATEMENTS:
                result = session.execute(text(statement))
                row_count = cast(CursorResult[Any], result).rowcount
                if row_count > 0:
                    affected_rows += row_count
        logger.info("ETL completed", extra={"affected_rows": affected_rows})
        return affected_rows
    except Exception:
        with session_scope(session_factory) as session:
            session.execute(
                text(
                    "UPDATE etl.job_run SET status='failed', finished_at=UTC_TIMESTAMP() "
                    "WHERE job_name='daily_price_etl' AND status='running'"
                )
            )
        logger.exception("ETL failed")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    run_etl()

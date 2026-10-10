from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.common.config import get_settings


def create_db_engine(url: str | None = None) -> Engine:
    return create_engine(
        url or get_settings().mysql_url,
        pool_pre_ping=True,
        pool_recycle=1800,
        future=True,
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)


@contextmanager
def session_scope(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def check_database(engine: Engine) -> dict[str, bool]:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1")).scalar()
    return {"database": result == 1}

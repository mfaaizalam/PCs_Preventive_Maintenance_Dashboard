from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    # Persistent connections kept open + how many extra can be opened
    # under burst load before requests start queuing. Sized for a lab
    # with up to ~60 PCs reporting every ~10s plus dashboard traffic.
    # Bump pool_size if you have more PCs than that.
    pool_size=20 if not is_sqlite else 5,
    max_overflow=20 if not is_sqlite else 0,
    # Don't wait forever for a free connection - fail fast instead of
    # silently stacking up latency.
    pool_timeout=10,
    # Recycle connections periodically so Postgres/network idle
    # timeouts don't hand back a dead connection.
    pool_recycle=1800,
    connect_args=(
        {"check_same_thread": False} if is_sqlite else {}
    ),
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
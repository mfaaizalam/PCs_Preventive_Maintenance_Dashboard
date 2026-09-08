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
    # Neon (serverless Postgres) suspends its compute after a few
    # minutes of inactivity and silently drops any connection that
    # was sitting idle when it did. pool_pre_ping catches a dead
    # connection AT CHECKOUT, but a connection can still die mid-use
    # if Neon suspends between two queries in the same request.
    # Recycling every 5 minutes forces SQLAlchemy to open a fresh
    # connection before Neon's own idle timeout has a chance to kill
    # the old one - fewer "server closed the connection" errors and
    # fewer cold-start stalls, though not a 100% guarantee.
    pool_recycle=300 if not is_sqlite else -1,
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
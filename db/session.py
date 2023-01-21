from sqlalchemy import event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import db.name

engine = create_async_engine(
    f'sqlite+aiosqlite:///{db.name.DB_FILENAME}')


# add enforcement for foreign keys
@event.listens_for(engine.sync_engine, "connect")
def enable_sqlite_fks(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

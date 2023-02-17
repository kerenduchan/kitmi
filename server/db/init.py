from sqlalchemy import event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import db.name
import db.globals


def init_db() -> None:

    # _create_db_file(db.name.DB_FILENAME)

    print("starting engine using DB file", db.name.DB_FILENAME)

    db.globals.engine = create_async_engine(
        f'sqlite+aiosqlite:///{db.name.DB_FILENAME}')

    # add enforcement for foreign keys
    @event.listens_for(db.globals.engine.sync_engine, "connect")
    def enable_sqlite_fks(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    db.globals.session_maker = sessionmaker(
        bind=db.globals.engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

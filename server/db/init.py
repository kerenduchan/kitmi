from pathlib import Path
from sqlalchemy import event, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import crypto
import db.name
import db.globals
import db.schema


def init_db() -> None:

    crypto.Crypto.generate_key()
    _create_db_file(db.name.DB_FILENAME)

    print(f'Creating DB engine ({db.name.DB_FILENAME})')

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


def _create_db_file(filename):
    """ create the db file if it doesn't exist """
    path = Path(filename)
    if not path.is_file():
        print(f'Creating DB ({filename})')
        sync_engine = create_engine(f'sqlite+pysqlite:///{filename}')
        db.schema.Base.metadata.create_all(sync_engine)
        sync_engine.dispose()

import sqlalchemy.ext.asyncio
import sqlalchemy.orm
import db.name
import contextlib
import typing

engine = sqlalchemy.ext.asyncio.create_async_engine(
    f'sqlite+aiosqlite:///{db.name.DB_FILENAME}', echo=True
)

SessionMaker = sqlalchemy.orm.sessionmaker(
    bind=engine,
    class_=sqlalchemy.ext.asyncio.AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

import sqlalchemy.ext.asyncio
import sqlalchemy.orm
import db.name
import contextlib
import typing

engine = sqlalchemy.ext.asyncio.create_async_engine(
    f'sqlite+aiosqlite:///{db.name.DB_FILENAME}'
)

async_session = sqlalchemy.orm.sessionmaker(
    bind=engine,
    class_=sqlalchemy.ext.asyncio.AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@contextlib.asynccontextmanager
async def get_session() -> typing.AsyncGenerator[sqlalchemy.ext.asyncio.AsyncSession, None]:
    async with async_session() as session:
        async with session.begin():
            try:
                yield session
            finally:
                await session.close()

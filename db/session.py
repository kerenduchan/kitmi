import sqlalchemy.ext.asyncio
import sqlalchemy.orm
import db.name

engine = sqlalchemy.ext.asyncio.create_async_engine(
    f'sqlite+aiosqlite:///{db.name.DB_FILENAME}')

SessionMaker = sqlalchemy.orm.sessionmaker(
    bind=engine,
    class_=sqlalchemy.ext.asyncio.AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

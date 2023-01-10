import asyncio
import sqlalchemy.ext.asyncio
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import random

Base = sqlalchemy.ext.declarative.declarative_base()


class Item(Base):
    __tablename__ = "items"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    data = sqlalchemy.Column(sqlalchemy.Integer)


async def chunk_generator(async_result, chunk_size):
    chunk = await async_result.fetchmany(chunk_size)
    while len(chunk) > 0:
        yield chunk
        chunk = await async_result.fetchmany(chunk_size)


async def test():

    # The DB engine
    engine = sqlalchemy.ext.asyncio.create_async_engine(
        f'sqlite+aiosqlite:///test/test_pagination.db')

    # Maker of async DB sessions
    session_maker = sqlalchemy.orm.sessionmaker(
        bind=engine,
        class_=sqlalchemy.ext.asyncio.AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    # Init the DB
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Fill a list with 10,007 values
    data = [random.randint(1, 1000000) for i in range(10007)]

    # Fill the 'items' table in the DB with these values
    async with session_maker() as session:
        session.add_all([Item(id=i, data=j) for i, j in enumerate(data, 1)])
        await session.commit()

    # read the items from the DB chunk-by-chunk using the streaming API
    async with engine.connect() as conn:
        async_result = await conn.stream(sqlalchemy.select(Item))

        chunk_size = 20
        count = 0
        chunks = chunk_generator(async_result, chunk_size)
        async for chunk in chunks:
            print(f"chunk: {chunk}")
            count += len(chunk)

        print(f'count={count}')
        await async_result.close()

    # Cleanup
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test())

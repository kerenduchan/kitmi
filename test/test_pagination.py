import asyncio
import sqlalchemy.ext.asyncio
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import random
import typing
import crypto

Base = sqlalchemy.ext.declarative.declarative_base()


class Item(Base):
    __tablename__ = "items"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    data = sqlalchemy.Column(sqlalchemy.Integer)

    def __repr__(self):
        return f'{self.id}={self.data}'


class Chunk:
    def __init__(self, recs: typing.List[Item], cursor_prev, cursor_next):
        self.recs = recs
        self.cursor_prev = cursor_prev
        self.cursor_next = cursor_next

    def __repr__(self):
        recs_str = 'EMPTY'
        if len(self.recs) > 0:
            recs_str = f'{self.recs[0].id}-{self.recs[len(self.recs) - 1].id}'
        s = f'{recs_str} ' \
            f' prev=({self.get_decrypted_cursor(self.cursor_prev)}) ' \
            f'next=({self.get_decrypted_cursor(self.cursor_next)})'
        return s

    @staticmethod
    def get_decrypted_cursor(cursor):
        if cursor is None:
            return 'None'
        elif cursor == '':
            return ''
        return crypto.Crypto().decrypt(cursor)


async def get_next_chunk_of_items(session, chunk_size, cursor=''):

    if cursor is None:
        return Chunk([], None, None)

    c = crypto.Crypto()
    decrypted_cursor = 0
    if cursor != '':
        decrypted_cursor = int(c.decrypt(cursor))

    # get one rec extra to determine whether there's a next chunk
    sql = sqlalchemy.select(Item).where(Item.id > decrypted_cursor).order_by(Item.id).limit(chunk_size + 1)
    recs = (await session.execute(sql)).scalars().all()

    cursor_next = None
    if len(recs) > chunk_size:
        last_id = recs[chunk_size - 1].id
        cursor_next = c.encrypt(str(last_id))
        # remove the extra item from the end of the list
        recs = recs[:-1]

    chunk = Chunk(recs, cursor, cursor_next)
    return chunk


async def get_prev_chunk_of_items(session, chunk_size, cursor=''):
    if cursor == '':
        return Chunk([], None, '')

    c = crypto.Crypto()
    decrypted_cursor = 0
    if cursor != '':
        decrypted_cursor = int(c.decrypt(cursor))

    sql = sqlalchemy.select(Item).where(Item.id <= decrypted_cursor).order_by(Item.id.desc()).limit(chunk_size + 1)
    recs = (await session.execute(sql)).scalars().all()
    recs.reverse()

    cursor_prev = ''
    if len(recs) > chunk_size:
        first_id = recs[0].id
        cursor_prev = c.encrypt(str(first_id))
        # remove the extra item from the beginning of the list
        recs = recs[1:]
    c = Chunk(recs, cursor_prev, cursor)
    return c


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

    # Fill a list with values
    data = [random.randint(1, 100) for i in range(101)]

    # Fill the 'items' table in the DB with these values
    async with session_maker() as session:
        session.add_all([Item(id=i, data=j) for i, j in enumerate(data, 1)])
        await session.commit()

        chunk_size = 10
        print(f'{chunk_size=}')
        cursor = ''

        chunk = None
        while cursor is not None:
            chunk = await get_next_chunk_of_items(session, chunk_size, cursor)
            print(chunk)
            cursor = chunk.cursor_next

        print('REACHED END. GOING BACK.')
        cursor = chunk.cursor_prev
        while cursor != '':
            chunk = await get_prev_chunk_of_items(session, chunk_size, cursor)
            print(chunk)
            cursor = chunk.cursor_prev

    # Cleanup
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test())

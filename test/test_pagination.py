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


GenericType = typing.TypeVar('GenericType')


# one page in the pagination
class Page:
    def __init__(self, items: typing.List[GenericType], prev, next_):
        self.items = items
        self.prev = prev
        self.next = next_

    def has_next(self):
        return self.next is not None

    def has_prev(self):
        return self.prev is not None

    def __repr__(self):
        items_str = 'EMPTY'
        if len(self.items) > 0:
            items_str = f'{self.items[0].id}-{self.items[len(self.items) - 1].id}'
        return f'{items_str} start=({self.get_decrypted_cursor(self.prev)}) ' \
               f'end=({self.get_decrypted_cursor(self.next)})'

    @staticmethod
    def get_decrypted_cursor(cursor):
        if cursor is None:
            return None
        return crypto.Crypto().decrypt(cursor)


async def get_next_items(session, page_size, cursor=None):

    # If cursor is None, get the first page of items. Otherwise, get
    # a page of items starting at the cursor.
    # Get one rec extra to determine whether there's a next page

    sql = sqlalchemy.select(Item)

    if cursor is not None:
        decrypted_cursor = int(crypto.Crypto().decrypt(cursor))
        sql = sql.where(Item.id > decrypted_cursor)

    sql = sql.order_by(Item.id).limit(page_size + 1)
    recs = (await session.execute(sql)).scalars().all()

    end_cursor = None
    if len(recs) > page_size:
        last_id = recs[page_size - 1].id
        end_cursor = crypto.Crypto().encrypt(str(last_id))
        # remove the extra item from the end of the list
        recs = recs[:-1]

    return Page(recs, cursor, end_cursor)


async def get_prev_items(session, page_size, cursor=None):

    # If cursor is None, get the last page of items. Otherwise, get
    # a page of items ending at the cursor.
    # Get one rec extra to determine whether there's a next page

    sql = sqlalchemy.select(Item)

    if cursor is not None:
        decrypted_cursor = int(crypto.Crypto().decrypt(cursor))
        sql = sql.where(Item.id <= decrypted_cursor)

    sql = sql.order_by(Item.id.desc()).limit(page_size + 1)
    recs = (await session.execute(sql)).scalars().all()
    recs.reverse()

    start_cursor = None
    if len(recs) > page_size:
        first_id = recs[0].id
        start_cursor = crypto.Crypto().encrypt(str(first_id))
        # remove the extra item from the beginning of the list
        recs = recs[1:]

    return Page(recs, start_cursor, cursor)


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

        page_size = 10
        print(f'{page_size=}')

        # get the first page
        page = await get_next_items(session, page_size)
        print(page)

        while page.has_next():
            page = await get_next_items(session, page_size, page.next)
            print(page)

        print('REACHED END. GOING BACK.')

        while page.has_prev():
            page = await get_prev_items(session, page_size, page.prev)
            print(page)

    # Cleanup
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test())

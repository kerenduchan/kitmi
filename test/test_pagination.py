import asyncio
import sqlalchemy.ext.asyncio
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import typing
import crypto
import sys

Base = sqlalchemy.ext.declarative.declarative_base()


class Book(Base):
    __tablename__ = "books"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String)

    def __repr__(self):
        return f"{self.id}='{self.title}'"


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
        return f'PAGE: {self.items} ' \
               f'prev=({self.get_decrypted_cursor(self.prev)}) ' \
               f'next=({self.get_decrypted_cursor(self.next)}) ' \
               f'has_prev={self.has_prev()} ' \
               f'has_next={self.has_next()} '

    @staticmethod
    def get_decrypted_cursor(cursor):
        if cursor is None:
            return None
        return crypto.Crypto().decrypt(cursor)


async def get_next_page_of_books(session, page_size, cur_page=None):
    return await get_next_page(session, "Book", "id", page_size, cur_page)


async def get_prev_page_of_books(session, page_size, cur_page=None):
    return await get_prev_page(session, "Book", "id", page_size, cur_page)


# cursor_column_name MUST be unique (for the cursor to not skip entries)
# and indexed (for efficient order_by)
async def get_next_page(
        session,
        class_name,
        cursor_column_name,
        page_size,
        cur_page=None):

    cursor = None if cur_page is None else cur_page.next

    db_schema_class = getattr(sys.modules[__name__], class_name)
    cursor_column = getattr(db_schema_class, cursor_column_name)

    # If cursor is None, get the first page of items. Otherwise, get
    # a page of items starting at the cursor.
    # Get one rec extra to determine whether there's a next page
    sql = sqlalchemy.select(db_schema_class)

    if cursor is not None:
        decrypted_cursor = int(crypto.Crypto().decrypt(cursor))
        sql = sql.where(cursor_column > decrypted_cursor)

    sql = sql.order_by(cursor_column).limit(page_size + 1)
    recs = (await session.execute(sql)).scalars().all()

    new_next = None
    if len(recs) > page_size:
        last_id = recs[page_size - 1].id
        new_next = crypto.Crypto().encrypt(str(last_id))
        # remove the extra item from the end of the list
        recs = recs[:-1]

    return Page(recs, cursor, new_next)


# cursor_column_name MUST be unique (for the cursor to not skip entries)
# and indexed (for efficient order_by)
async def get_prev_page(
        session,
        class_name,
        cursor_column_name,
        page_size,
        cur_page=None):

    cursor = None if cur_page is None else cur_page.prev

    db_schema_class = getattr(sys.modules[__name__], class_name)
    cursor_column = getattr(db_schema_class, cursor_column_name)

    # If cursor is None, get the last page of items. Otherwise, get
    # a page of items ending at the cursor.
    # Get one rec extra to determine whether there's a next page
    sql = sqlalchemy.select(db_schema_class)

    if cursor is not None:
        decrypted_cursor = int(crypto.Crypto().decrypt(cursor))
        sql = sql.where(cursor_column <= decrypted_cursor)

    sql = sql.order_by(cursor_column.desc()).limit(page_size + 1)
    recs = (await session.execute(sql)).scalars().all()
    recs.reverse()

    new_prev = None
    if len(recs) > page_size:
        first_id = recs[0].id
        new_prev = crypto.Crypto().encrypt(str(first_id))
        # remove the extra item from the beginning of the list
        recs = recs[1:]

    return Page(recs, new_prev, cursor)


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

    books_count = 101

    # Fill the 'items' table in the DB with these values
    async with session_maker() as session:
        session.add_all([Book(id=i, title=f'Title {i}') for i in range(1, books_count + 1)])
        await session.commit()

        page_size = 10
        print(f'{books_count=} {page_size=}')

        page = None
        while True:
            page = await get_next_page_of_books(session, page_size, page)
            print(page)
            if not page.has_next():
                break

        print('\nREACHED END. GOING BACK.')

        while True:
            page = await get_prev_page_of_books(session, page_size, page)
            print(page)
            if not page.has_prev():
                break

        print('\nSTARTING AT THE END THIS TIME.')

        # get the last page
        page = None
        while True:
            page = await get_prev_page_of_books(session, page_size, page)
            print(page)
            if not page.has_prev():
                break

        print('REACHED BEGINNING. GOING TO THE END.')

        while True:
            page = await get_next_page_of_books(session, page_size, page)
            print(page)
            if not page.has_next():
                break

    # Cleanup
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test())

from typing import List
import datetime
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from db.schema import Transaction, Payee
import db.utils
from db.transactions_filter import TransactionsFilter
from db.pagination_window import PaginationWindow


async def get_all_transaction_ids(
        session: AsyncSession,
        account_id: int,
        start_date: datetime.date) -> List[Transaction]:
    """ Get the IDs of all transactions from the db that belong
    to the given account ID and are newer than the given date. """
    sql = sqlalchemy.select(Transaction.id). \
        where(Transaction.account_id == account_id)
    if start_date is not None:
        sql = sql.where(Transaction.date >= start_date)
    res = await session.execute(sql)
    recs = res.scalars().all()
    return recs


async def get_transactions(
        session: AsyncSession,
        order_by: str,
        db_filter: TransactionsFilter | None = None,
        limit: int | None = None,
        offset: int = 0) -> PaginationWindow:
    """
    Get one pagination window of transactions for the given limit
    and offset, ordered by the given attribute and filtered using the
    given filters
    """

    order_by_column = getattr(Transaction, order_by)

    # get the items in the pagination window
    sql = sqlalchemy.select(Transaction) if db_filter is None or db_filter.categorized is None \
        else sqlalchemy.select(Transaction, Payee)

    sql = sql.order_by(order_by_column).limit(limit).offset(offset)

    if db_filter:
        sql = db_filter.apply(sql)

    res = await session.execute(sql)
    items = res.scalars().all()

    # get the total items count
    sql = sqlalchemy.select([sqlalchemy.func.count()])

    sql = sql.select_from(Transaction) if db_filter is None or db_filter.categorized is None \
        else sql.select_from(Transaction, Payee)

    if db_filter:
        sql = db_filter.apply(sql)

    res = await session.execute(sql)
    total_items_count = res.scalar()

    return PaginationWindow(
        items=items,
        total_items_count=total_items_count
    )


async def update_transaction(
        session: AsyncSession,
        transaction_id: int,
        override_subcategory: bool | None = None,
        subcategory_id: int  | None = None,
        note: str | None = None) -> db.schema.Transaction:

    values = {
        'override_subcategory': override_subcategory,
        'subcategory_id': subcategory_id,
        'note': note
    }

    return await db.utils.update(
        session, db.schema.Transaction, transaction_id, values)

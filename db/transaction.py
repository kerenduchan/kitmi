from typing import List
import datetime
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
import db.schema
import db.utils


async def get_all_transaction_ids(
        session: AsyncSession,
        account_id: int,
        start_date: datetime.date) -> List[db.schema.Transaction]:
    """ Get the IDs of all transactions from the db that belong
    to the given account ID and are newer than the given date. """
    sql = sqlalchemy.select(db.schema.Transaction.id). \
        where(db.schema.Transaction.account_id == account_id)
    if start_date is not None:
        sql = sql.where(db.schema.Transaction.date >= start_date)
    res = await session.execute(sql)
    recs = res.scalars().all()
    return recs


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

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from db.schema import Transaction
import db.utils


async def get_all_transaction_ids(session, account_id, start_date):
    """ Get the IDs of all transactions from the db that belong
    to the given account ID and are newer than the given date. """
    sql = sqlalchemy.select(Transaction.id). \
        where(Transaction.account_id == account_id)
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
        note: str | None = None) -> Transaction:

    values = {
        'override_subcategory': override_subcategory,
        'subcategory_id': subcategory_id,
        'note': note
    }

    return await db.utils.update(
        session, db.schema.Transaction, transaction_id, values)

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy.dialects.sqlite
from db.schema import Payee
import db.utils


async def create_payees_ignore_conflict(session, names):
    """ Insert the given payee names into the payees table,
    if they don't already exist. """

    if len(names) == 0:
        # nothing to do
        return

    # INSERT INTO payees VALUES ... ON CONFLICT DO NOTHING
    stmt = (sqlalchemy.dialects.sqlite.insert(db.schema.Payee)).on_conflict_do_nothing()
    values = [{'name': n} for n in names]
    await session.execute(stmt, values)
    await session.commit()


async def create_payee(
        session: AsyncSession,
        name: str,
        subcategory_id: int | None = None,
        note: str = "") -> Payee:

    # don't allow empty name for payee
    db.utils.test_not_empty(name, "Payee name")

    rec = Payee(
        name=name,
        subcategory_id=subcategory_id,
        note=note)
    return await db.utils.create(session, rec)


async def update_payee(
        session: AsyncSession,
        payee_id: int,
        name: str | None = None,
        subcategory_id: int | None = None,
        note: str | None = None) -> Payee:

    # don't allow empty name for payee
    db.utils.test_not_empty(name, "Payee name")

    values = {
        'name': name,
        'subcategory_id': subcategory_id,
        'note': note,
    }

    return await db.utils.update(
        session, Payee, payee_id, values)

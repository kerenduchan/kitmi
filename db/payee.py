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
        subcategory_id: int | None,
        name: str | None = None,
        note: str | None = None) -> Payee:

    # don't allow empty name for payee
    db.utils.test_not_empty(name, "Payee name")

    # None for subcategory_id doesn't mean don't update,
    # it means update to be null
    values = {'subcategory_id': subcategory_id}

    if name is not None:
        values['name'] = name

    if note is not None:
        values['note'] = note

    return await db.utils.update_values(
        session, Payee, payee_id, values)


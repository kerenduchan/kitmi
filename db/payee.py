from sqlalchemy.ext.asyncio import AsyncSession
from db.schema import Payee
import db.utils


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

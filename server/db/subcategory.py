import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from db.schema import Subcategory, Payee, Transaction
import db.utils


async def create_subcategory(
        session: AsyncSession,
        name: str,
        category_id: int) -> Subcategory:

    # don't allow empty name for subcategory
    db.utils.test_not_empty(name, "Subcategory name")

    rec = Subcategory(
        name=name,
        category_id=category_id)
    return await db.utils.create(session, rec)


async def update_subcategory(
        session: AsyncSession,
        subcategory_id: int,
        name: str | None = None,
        category_id: int | None = None) -> Subcategory:

    # don't allow empty name for subcategory
    db.utils.test_not_empty(name, "Subcategory name")

    values = {
        'name': name,
        'category_id': category_id
    }

    return await db.utils.update(
        session, Subcategory, subcategory_id, values)


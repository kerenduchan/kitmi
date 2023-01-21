import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from db.schema import Category, Subcategory
import db.utils


async def create_category(
        session: AsyncSession,
        name: str,
        is_expense: bool = True,
        exclude_from_reports: bool = False) -> Category:

    # don't allow empty name for category
    db.utils.test_not_empty(name, "Category name")

    order = await _get_largest_category_order(session) + 1

    rec = Category(
        name=name,
        is_expense=is_expense,
        exclude_from_reports=exclude_from_reports,
        order=order)
    return await db.utils.create(session, rec)


async def update_category(
        session: AsyncSession,
        category_id: int,
        name: str | None = None,
        is_expense: bool | None = None,
        exclude_from_reports: bool | None = None) -> Category:

    # don't allow empty name for category
    db.utils.test_not_empty(name, "Category name")

    values = {
        'name': name,
        'is_expense': is_expense,
        'exclude_from_reports': exclude_from_reports
    }

    return await db.utils.update(
        session, Category, category_id, values)


async def delete_category(
        session: AsyncSession,
        category_id: int) -> int:
    # check if this author has any books
    sql = sqlalchemy.select(Subcategory).\
        where(Subcategory.category_id == category_id).limit(1)
    res = await session.execute(sql)
    is_in_use = res.first()

    if is_in_use:
        raise Exception('cannot delete a category that has subcategories')

    return await db.utils.delete(session, Category, category_id)


async def move_category(
        session: AsyncSession,
        category_id: int,
        is_down: bool) -> Category:

    # get all categories from the db, ordered by "order"
    sql = sqlalchemy.select(Category).order_by(Category.order)
    res = await session.execute(sql)
    categories = res.scalars().all()

    # check that a category with this category_id exists
    found = [index for index, c in enumerate(categories) if c.id == category_id]
    if not found:
        raise Exception(f"category with id '{category_id}' does not exist.")

    index = found[0]

    # check whether there's any category above/below it (depending on is_down)
    if is_down:
        if index == len(categories) - 1:
            raise Exception(f"category with id '{category_id}' cannot be moved any further down")
    elif index == 0:
        raise Exception(f"category with id '{category_id}' cannot be moved any further up")

    # get the order of the category, and the category below/above it
    # (according to the given is_down)
    current_order = categories[index].order
    swap_index = index + 1 if is_down else index - 1
    new_order = categories[swap_index].order

    # swap order values between this category and the one below/above it
    sql = sqlalchemy.update(Category) \
        .where(Category.order == new_order) \
        .values(order=current_order)
    await session.execute(sql)

    sql = sqlalchemy.update(Category) \
        .where(Category.id == category_id) \
        .values(order=new_order)
    await session.execute(sql)

    await session.commit()

    return categories[index]


async def _get_largest_category_order(session):
    window = await db.utils.get(session, Category, "order")
    categories = window.items
    if len(categories) == 0:
        return 0
    return categories[len(categories) - 1].order

import strawberry
from api.account import Account, AccountSource
from api.category import Category
from api.subcategory import Subcategory
from api.payee import Payee
from api.transaction import Transaction
from api.count import Count
from db.session import session_maker
import db.category
import db.subcategory
import db.payee
import db.account
import db.transaction
import db.schema

# ---------------------------------------------------------------
# account


async def create_account(
        name: str,
        source: AccountSource,
        username: str,
        password: str) -> Account:
    async with session_maker() as session:
        rec = await db.account.create_account(
            session=session,
            name=name,
            source=db.schema.AccountSource(source.value),
            username=username,
            password=password)
        return Account.from_db(rec)


async def update_account(
        account_id: strawberry.ID,
        name: str | None = None,
        source: AccountSource | None = None,
        username: str | None = None,
        password: str | None = None) -> Account:

    async with session_maker() as session:
        rec = await db.account.update_account(
            session=session,
            account_id=account_id,
            name=name,
            source=db.schema.AccountSource(source.value),
            username=username,
            password=password)
        return Account.from_db(rec)


async def delete_account(account_id: strawberry.ID) -> Count:
    async with session_maker() as session:
        count = await db.account.delete_account(session, account_id)
        return Count(count=count)

# ---------------------------------------------------------------
# category


async def create_category(
        name: str,
        is_expense: bool = True,
        exclude_from_reports: bool = False) -> Category:
    async with session_maker() as session:
        rec = await db.category.create_category(
            session=session,
            name=name,
            is_expense=is_expense,
            exclude_from_reports=exclude_from_reports)
        return Category.from_db(rec)


async def update_category(
        category_id: strawberry.ID,
        name: str | None = None,
        is_expense: bool | None = None,
        exclude_from_reports: bool | None = None) -> Category:

    async with session_maker() as session:
        rec = await db.category.update_category(
            session, category_id, name, is_expense, exclude_from_reports)
        return Category.from_db(rec)


async def delete_category(category_id: strawberry.ID) -> Count:
    async with session_maker() as session:
        count = await db.category.delete_category(session, category_id)
        return Count(count=count)


async def move_category_up(category_id: strawberry.ID) -> Category:
    async with session_maker() as session:
        rec = await db.category.move_category(session, category_id, is_down=False)
        return Category.from_db(rec)


async def move_category_down(category_id: strawberry.ID) -> Category:
    async with session_maker() as session:
        rec = await db.category.move_category(session, category_id, is_down=True)
        return Category.from_db(rec)

# ---------------------------------------------------------------
# subcategory


async def create_subcategory(
        name: str,
        category_id: strawberry.ID) -> Subcategory:
    async with session_maker() as session:
        rec = await db.subcategory.create_subcategory(
            session=session,
            name=name,
            category_id=category_id)
        return Subcategory.from_db(rec)


async def update_subcategory(
        subcategory_id: strawberry.ID,
        name: str | None = None,
        category_id: strawberry.ID | None = None) -> Subcategory:

    async with session_maker() as session:
        rec = await db.subcategory.update_subcategory(
            session, subcategory_id, name, category_id)
        return Subcategory.from_db(rec)


async def delete_subcategory(subcategory_id: strawberry.ID) -> Count:
    async with session_maker() as session:
        count = await db.subcategory.delete_subcategory(session, subcategory_id)
        return Count(count=count)

# ---------------------------------------------------------------
# payee


async def create_payee(
        name: str,
        subcategory_id: strawberry.ID | None = None,
        note: str = "") -> Payee:
    async with session_maker() as session:
        rec = await db.payee.create_payee(
            session=session,
            name=name,
            subcategory_id=subcategory_id,
            note=note)
        return Payee.from_db(rec)


async def update_payee(
        payee_id: strawberry.ID,
        name: str | None = None,
        subcategory_id: strawberry.ID | None = None,
        note: str | None = None) -> Payee:

    async with session_maker() as session:
        rec = await db.payee.update_payee(
            session=session,
            payee_id=payee_id,
            name=name,
            subcategory_id=subcategory_id,
            note=note)
        return Payee.from_db(rec)

# ---------------------------------------------------------------
# transaction


async def update_transaction(
        transaction_id: strawberry.ID,
        override_subcategory: bool | None = None,
        subcategory_id: strawberry.ID | None = None,
        note: str | None = None) -> Transaction:

    async with session_maker() as session:
        rec = await db.transaction.update_transaction(
            session=session,
            transaction_id=transaction_id,
            override_subcategory=override_subcategory,
            subcategory_id=subcategory_id,
            note=note)
        return Transaction.from_db(rec)

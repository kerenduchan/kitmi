import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from db.schema import Account, AccountSource, Transaction
import db.utils
from crypto import Crypto


async def create_account(
        session: AsyncSession,
        name: str,
        source: AccountSource,
        username: str,
        password: str) -> Account:

    # don't allow empty name for account
    db.utils.test_not_empty(name, "Account name")

    rec = Account(
        name=name,
        source=source,
        username=Crypto().encrypt(username),
        password=Crypto().encrypt(password))

    rec = await db.utils.create(session, rec)
    return rec


async def update_account(
        session: AsyncSession,
        account_id: str,
        name: str | None = None,
        source: AccountSource | None = None,
        username: str | None = None,
        password: str | None = None) -> Account:

    # don't allow empty name for account
    db.utils.test_not_empty(name, "Account name")

    values = {
        'name': name,
        'source': source,
        'username': Crypto().encrypt(username) if username is not None else None,
        'password': Crypto().encrypt(password) if password is not None else None
    }

    return await db.utils.update(
        session, Account, account_id, values)


async def delete_account(
        session: AsyncSession,
        account_id: str) -> int:
    # check if this account has any transactions
    sql = sqlalchemy.select(Transaction).\
        where(Transaction.account_id == account_id).limit(1)
    res = await session.execute(sql)
    is_in_use = res.first()

    if is_in_use:
        raise Exception('cannot delete an account that has transactions')

    return await db.utils.delete(session, Account, account_id)

import datetime
import uuid
import logging
import asyncio
import db.account
import db.schema
from db.session import session_maker
import db.payee

import init_logging

transactions = [
    {'date': '2022-01-01', 'amount': -20},
    {'date': '2022-02-02', 'amount': -40},
    {'date': '2022-03-15', 'amount': -70},
]

payees = [
    'payee1',
    'payee2'
]


async def create_payees(session):
    payee_ids = []
    for p in payees:
        payee = await db.payee.create_payee(session, p)
        payee_ids.append(payee.id)
    return payee_ids


async def create_transactions(session, account_id, payee_ids):
    idx = 0
    for t in transactions:
        rec = db.schema.Transaction(
            id=str(uuid.uuid4()),
            date=datetime.date.fromisoformat(t['date']),
            amount=t['amount'],
            account_id=account_id,
            payee_id=payee_ids[idx])
        session.add(rec)
        idx += 1
        idx = idx % len(payee_ids)

    await session.commit()


async def main():

    try:
        init_logging.init_logging()

        async with session_maker() as session:
            account = await db.account.create_account(
                session,
                "fake1",
                db.schema.AccountSource.max,
                "keren",
                "password")

            payee_ids = await create_payees(session)

            await create_transactions(session, account.id, payee_ids)

    except Exception as e:
        logging.exception(str(e))
        raise e

if __name__ == "__main__":
    asyncio.run(main())

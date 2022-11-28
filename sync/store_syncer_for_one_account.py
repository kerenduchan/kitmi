import datetime
import db.session
import db.ops
import db.schema
import sqlalchemy
import logging


class StoreSyncerForOneAccount:
    """ Fetches transactions from one account and updates the db accordingly. """

    def __init__(self, account, fetcher, payees):
        self._account = account
        self._fetcher = fetcher
        self._payees = payees

    async def sync(self, session):
        """ Sync the db for the account """

        start_date = self._determine_start_date()
        end_date = datetime.datetime.today().date()

        # Load all transaction ids for this account newer than the start_date
        # (to avoid inserting duplicates)

        logging.debug(f"{self._account.name}: Getting all transaction IDs for this account starting at {start_date}")
        transaction_ids = await db.ops.get_all_transaction_ids(
            session, self._account.id, start_date)

        logging.info(f'{self._account.name}: Loaded {len(transaction_ids)} transaction IDs')
        if logging.DEBUG >= logging.root.level:
            for id_ in transaction_ids:
                logging.debug(f'{id_}')

        # Get the transactions for this account from the source
        logging.info(f"{self._account.name}: Fetching account data between {start_date} and {end_date}...")
        transactions = await self._fetcher.fetch(start_date, end_date)
        count = len(transactions)
        logging.info(f"{self._account.name}: Done fetching account data ({count} transactions).")

        # Filter out any transactions that have already been stored
        transactions = [t for t in transactions if t.id not in transaction_ids]
        logging.info(f"{self._account.name}: {len(transactions)} out of {count} transactions haven't already been stored")

        if len(transactions) > 0:
            # Store any new payees that appear in the fetched transactions
            await self._store_new_payees(session, transactions)

            # Store the new transactions
            await self._store_transactions(session, transactions, self._payees)

        # update last_synced for the account
        sql = sqlalchemy.update(db.schema.Account). \
            where(db.schema.Account.id == self._account.id).\
            values(last_synced=end_date)
        await session.execute(sql)

        await session.commit()

        print(f"{self._account.name}: Stored {len(transactions)} transactions")

    async def _store_new_payees(self, session, transactions):
        """ Store any new payees from the given transactions """

        # Set of all payees from the given transactions
        # minus the payees in the existing payees dict
        payee_names = {t.payee for t in transactions if t.payee not in self._payees}
        count = len(payee_names)
        if count == 0:
            logging.info(f"{self._account.name}: No new payees from transactions")
            return

        logging.info(f"{self._account.name}: Storing {count} new payees from transactions")

        # insert payees that weren't already in the db
        await db.ops.create_payees_ignore_conflict(session, payee_names)

        # reload these payees from the db
        sql = sqlalchemy.select(db.schema.Payee).where(db.schema.Payee.name.in_(payee_names))
        payees = (await session.execute(sql)).scalars().unique().all()

        # prepare a map of payee name to payee id
        payees = {p.name: p.id for p in payees}

        # update the payees dict
        self._payees.update(payees)

    async def _store_transactions(self, session, transactions, payees):
        """ Store the given transactions """

        db_transactions = []
        for t in transactions:
            db_transaction = \
                db.schema.Transaction(id=t.id,
                                      date=t.date,
                                      amount=t.amount,
                                      account_id=self._account.id,
                                      payee_id=payees[t.payee],
                                      subcategory_id=None)
            # TODO handle case where transaction with this ID is already in the db
            session.add(db_transaction)

        await session.commit()

    def _determine_start_date(self):
        if self._account.last_synced is None:
            return datetime.date(2022, 1, 1)

        return self._account.last_synced - datetime.timedelta(days=30)

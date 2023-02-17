from typing import List
import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
import db.globals
from db.schema import Payee, Account
from db.utils import get_all
from sync.store_syncer_for_one_account import StoreSyncerForOneAccount
from fetch.i_account_data_fetcher import IAccountDataFetcher


class StoreSyncer:
    """ Fetches transactions from all accounts and updates the db accordingly. """
    _session: AsyncSession
    _fetchers: List[IAccountDataFetcher]

    def __init__(
            self,
            session: AsyncSession,
            fetchers: List[IAccountDataFetcher]):
        self._session = session
        self._fetchers = fetchers

    async def sync(self):
        """ Sync the db for each of the given fetchers """

        # load all accounts and payees from db
        logging.info('Loading accounts and payees from the db')
        (accounts, payees) = await asyncio.gather(
            get_all(self._session, Account),
            get_all(self._session, Payee)
        )

        logging.info(f'Loaded {len(accounts)} accounts and {len(payees)} payees')

        if logging.DEBUG >= logging.root.level:
            logging.debug(f'{len(accounts)} accounts:')
            for a in accounts:
                logging.debug(f'{a}')

            logging.debug(f'{len(payees)} payees:')
            for p in payees:
                logging.debug(f'{p}')

        # prepare a map of account id to account
        accounts = {a.id: a for a in accounts}

        # prepare a map of payee name to payee id
        payees = {p.name: p.id for p in payees}

        # sync each fetcher concurrently
        syncers = []
        for fetcher in self._fetchers:
            account = accounts[fetcher.get_account_id()]
            syncer = StoreSyncerForOneAccount(account, fetcher, payees)
            syncers.append(syncer)

        await asyncio.gather(*[
            StoreSyncer._sync_one_account(syncer) for syncer in syncers])

    @staticmethod
    async def _sync_one_account(syncer: StoreSyncerForOneAccount) -> None:
        # since this is done concurrently,
        # need to create a separate session for each
        async with db.globals.session_maker() as session:
            await syncer.sync(session)

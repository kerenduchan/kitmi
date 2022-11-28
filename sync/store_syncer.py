import logging
import asyncio
import db.ops
import db.session
import sync.store_syncer_for_one_account


class StoreSyncer:
    """ Fetches transactions from all accounts and updates the db accordingly. """

    def __init__(self, session, fetchers):
        self._session = session
        self._fetchers = fetchers

    async def sync(self):
        """ Sync the db for each of the given fetchers """

        # load all accounts and payees from db
        logging.info('Loading accounts and payees from the db')
        (accounts, payees) = await asyncio.gather(
            db.ops.get_all(self._session, "Account", "id"),
            db.ops.get_all(self._session, "Payee", "id")
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
            syncer = \
                sync.store_syncer_for_one_account.StoreSyncerForOneAccount(
                    account, fetcher, payees)
            syncers.append(syncer)

        await asyncio.gather(*[
            StoreSyncer._sync_one_account(syncer) for syncer in syncers])

    @staticmethod
    async def _sync_one_account(syncer):
        # since this is done concurrently,
        # need to create a separate session for each
        async with db.session.SessionMaker() as session:
            await syncer.sync(session)

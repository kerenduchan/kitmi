from sqlalchemy.ext.asyncio import AsyncSession
import logging
from db.utils import get_all
from db.schema import Account
from fetch.israeli_bank_scraper_account_data_fetcher import IsraeliBankScraperAccountDataFetcher
import sync.store_syncer


async def do_sync(session: AsyncSession, scraper_script: str):

    logging.info('Starting sync')

    logging.debug('Loading all accounts from the db')
    accounts = await get_all(session, Account)

    logging.info(f'Loaded {len(accounts)} accounts:')
    for a in accounts:
        logging.info(a)

    # Create a list of concrete fetchers for all accounts
    fetchers = [IsraeliBankScraperAccountDataFetcher(
        scraper_script,
        a.id,
        a.source,
        a.username,
        a.password)
        for a in accounts]

    # sync the accounts for each of the given fetchers
    syncer = sync.store_syncer.StoreSyncer(session, fetchers)
    await syncer.sync()

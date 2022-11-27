import db.ops
import fetch.israeli_bank_scraper_account_data_fetcher
import sync.store_syncer
import crypto


async def do_sync(session, scraper_script):
    # Load all accounts from db

    accounts = await db.ops.get_all(session, "Account", "id")

    c = crypto.Crypto()

    # Create a list of concrete fetchers for all accounts
    fetchers = [fetch.israeli_bank_scraper_account_data_fetcher.IsraeliBankScraperAccountDataFetcher(
        scraper_script,
        a.id,
        a.source,
        c.decrypt(a.username),
        c.decrypt(a.password))
        for a in accounts]

    # sync the accounts for each of the given fetchers
    syncer = sync.store_syncer.StoreSyncer(session, fetchers)
    await syncer.sync()

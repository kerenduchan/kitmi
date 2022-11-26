class StoreSyncer:
    """ Fetches transactions from all accounts and updates the db accordingly. """

    def __init__(self, session, fetchers):
        self._session = session
        self._fetchers = fetchers

    async def sync(self):
        """ Sync the db for each of the given fetchers """
        print("sync...")

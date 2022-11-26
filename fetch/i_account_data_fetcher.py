import abc


class IAccountDataFetcher(abc.ABC):
    """ Base class for all account data fetchers """

    @abc.abstractmethod
    async def fetch(self, start_date, end_date=None):
        pass

    @abc.abstractmethod
    def get_account_id(self):
        pass

import abc
import datetime


class IAccountDataFetcher(abc.ABC):
    """ Base class for all account data fetchers """

    @abc.abstractmethod
    async def fetch(
            self,
            start_date: datetime.date,
            end_date: datetime.date = None):
        pass

    @abc.abstractmethod
    def get_account_id(self):
        pass

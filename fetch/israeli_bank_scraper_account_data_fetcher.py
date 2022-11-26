import json
import hashlib
import asyncio
import datetime
import dataclasses
import util
import fetch.i_account_data_fetcher


@dataclasses.dataclass
class Transaction:
    """ Represents one transaction received from the scraper """

    def __init__(self, rec):
        self.id = hashlib.sha1(repr(rec).encode('utf-8')).hexdigest()
        self.date = util.json_datetime_to_date(rec['date'])
        self.payee = rec['description']
        self.amount = rec['chargedAmount']

    def __repr__(self):
        return f'id={self.id} date={self.date} payee={self.payee} ' + \
               f'amount={self.amount}'


class IsraeliBankScraperAccountDataFetcher(fetch.i_account_data_fetcher.IAccountDataFetcher):
    """ Concrete fetcher that uses the scraper js tool to fetch transactions
    from one account."""

    def __init__(self, scraper_script, account_id, source, username, password):
        self._scraper_script = scraper_script
        self._account_id = account_id
        self._source = source
        self._username = username
        self._password = password

    def get_account_id(self):
        return self._account_id

    async def fetch(self, start_date, end_date=None):

        # adjust the end date to be today if none given
        if end_date is None:
            end_date = datetime.date.today()

        cmd_and_params = [
            'node',
            self._scraper_script,
            self._source,
            str(start_date),
            self._username,
            self._password]

        proc = await asyncio.create_subprocess_exec(
            *cmd_and_params,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError("Script failed. " + stderr.decode())

        # load the transactions from json
        data = json.loads(stdout.decode())

        # filter the desired date range
        data = [rec for rec in data
                if (util.is_in_range(rec['date'], start_date, end_date))]

        # create a list of Transaction instances from the fetched data
        transactions = [Transaction(rec) for rec in data]
        return transactions

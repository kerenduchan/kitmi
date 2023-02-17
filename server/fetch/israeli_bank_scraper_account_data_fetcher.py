from typing import List
import json
import hashlib
import asyncio
import datetime
import dataclasses
import db.schema
from crypto import Crypto
from fetch.i_account_data_fetcher import IAccountDataFetcher


@dataclasses.dataclass
class Transaction:
    """ Represents one transaction received from the scraper """
    id: str
    date: datetime.date
    payee: str
    amount: float

    def __init__(self, rec):
        self.id = hashlib.sha1(repr(rec).encode('utf-8')).hexdigest()
        self.date = rec['date']
        self.payee = rec['description']
        self.amount = rec['chargedAmount']

    def __repr__(self):
        return f'id={self.id} date={self.date} payee={self.payee} ' + \
               f'amount={self.amount}'


class IsraeliBankScraperAccountDataFetcher(IAccountDataFetcher):
    """ Concrete fetcher that uses the scraper js tool to fetch transactions
    from one account."""
    _scraper_script: str
    _account_id: int
    _source: db.schema.AccountSource
    _username: str
    _password: str

    def __init__(
            self,
            scraper_script: str,
            account_id: int,
            source: db.schema.AccountSource,
            username: str,
            password: str):
        self._scraper_script = scraper_script
        self._account_id = account_id
        self._source = source
        self._username = username
        self._password = password

    def get_account_id(self) -> int:
        return self._account_id

    async def fetch(
            self,
            start_date: datetime.date,
            end_date: datetime.date = None) -> List[Transaction]:

        # adjust the end date to be today if none given
        if end_date is None:
            end_date = datetime.date.today()

        cmd_and_params = [
            'node',
            self._scraper_script,
            self._source.value,
            str(start_date),
            Crypto().decrypt(self._username),
            Crypto().decrypt(self._password)]

        proc = await asyncio.create_subprocess_exec(
            *cmd_and_params,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError("Script failed. " + stderr.decode())

        # load the transactions from json
        data = json.loads(stdout.decode())

        # fix the date (add 1 day)
        for rec in data:
            wrong_date = datetime.date.fromisoformat(rec['date'][:10])
            rec['date'] = wrong_date + datetime.timedelta(1)

        # filter the desired date range
        data = [rec for rec in data
                if start_date <= rec['date'] <= end_date]

        # create a list of Transaction instances from the fetched data
        transactions = [Transaction(rec) for rec in data]
        return transactions

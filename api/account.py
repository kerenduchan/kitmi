from typing import List
from enum import Enum
import strawberry
from strawberry.types.info import Info
import db.schema
from api.transaction import Transaction
from crypto import Crypto


@strawberry.enum
class AccountSource(Enum):
    MAX = "max"
    LEUMI = "leumi"


@strawberry.type
class Account:
    id: strawberry.ID
    name: str
    source: AccountSource
    username: str

    @strawberry.field
    async def transactions(self, info: Info) -> List["Transaction"]:
        transactions = await info.context.dataloaders["transactions_by_account_id"].load(int(self.id))
        return [Transaction.marshal(t) for t in transactions]

    @staticmethod
    def from_db(obj: db.schema.Account) -> "Account":
        return Account(id=strawberry.ID(str(obj.id)),
                       name=obj.name,
                       source=obj.source.value,
                       username=obj.username)

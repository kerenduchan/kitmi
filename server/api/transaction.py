from typing import TYPE_CHECKING, Annotated, Optional
from datetime import date
import strawberry
from strawberry.types.info import Info
import db.schema
import api

if TYPE_CHECKING:
    from api.payee import Payee
    from api.account import Account
    from api.subcategory import Subcategory


@strawberry.type
class Transaction:
    id: strawberry.ID
    date: date
    amount: float
    account_id: strawberry.ID
    payee_id: strawberry.ID
    override_subcategory: bool
    subcategory_id: strawberry.ID | None
    note: str

    @strawberry.field
    async def payee(self, info: Info) -> Annotated["Payee", strawberry.lazy("api.payee")]:
        payee = await info.context.dataloaders["payee_by_id"].load(self.payee_id)
        return api.payee.Payee.from_db(payee)

    @strawberry.field
    async def account(self, info: Info) -> Annotated["Account", strawberry.lazy("api.account")]:
        account = await info.context.dataloaders["account_by_id"].load(self.account_id)
        return api.account.Account.from_db(account)

    @strawberry.field
    async def subcategory(self, info: Info) \
            -> Optional[Annotated["Subcategory", strawberry.lazy("api.subcategory")]]:
        if self.subcategory_id is None:
            return None
        s = await info.context.dataloaders["subcategory_by_id"].load(self.subcategory_id)
        return api.subcategory.Subcategory.from_db(s)

    @staticmethod
    def from_db(obj: db.schema.Transaction) \
            -> "Transaction":
        return Transaction(
            id=strawberry.ID(str(obj.id)),
            date=obj.date,
            amount=obj.amount,
            account_id=obj.account_id,
            payee_id=obj.payee_id,
            override_subcategory=obj.override_subcategory,
            subcategory_id=obj.subcategory_id,
            note=obj.note
        )

from typing import TYPE_CHECKING, Annotated, Optional, List
import strawberry
from strawberry.types.info import Info
import db.schema
import api

if TYPE_CHECKING:
    from api.subcategory import Subcategory
    from api.transaction import Transaction


@strawberry.type
class Payee:
    id: strawberry.ID
    name: str
    subcategory_id: strawberry.ID | None
    note: str

    @strawberry.field
    async def subcategory(self, info: Info) \
            -> Optional[Annotated["Subcategory", strawberry.lazy("api.subcategory")]]:
        if self.subcategory_id is None:
            return None
        subcategory = await info.context.dataloaders["subcategory_by_id"].load(self.subcategory_id)
        return api.subcategory.Subcategory.from_db(subcategory)

    @strawberry.field
    async def transactions(self, info: Info) \
            -> List[Annotated["Transaction", strawberry.lazy("api.transaction")]]:
        transactions = await info.context.dataloaders["transactions_by_payee_id"].load(self.id)
        return [Transaction.from_db(t) for t in transactions]

    @staticmethod
    def from_db(obj: db.schema.Payee) -> "Payee":
        return Payee(
            id=strawberry.ID(str(obj.id)),
            name=obj.name,
            subcategory_id=obj.subcategory_id,
            note=obj.note,
        )

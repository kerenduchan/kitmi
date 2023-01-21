from typing import TYPE_CHECKING, Annotated, List
import strawberry
from strawberry.types.info import Info
import api
import db.schema

if TYPE_CHECKING:
    from api.payee import Payee
    from api.category import Category


@strawberry.type
class Subcategory:
    id: strawberry.ID
    name: str
    category_id: strawberry.ID

    @strawberry.field
    async def category(self, info: Info) \
            -> Annotated["Category", strawberry.lazy("api.category")]:
        category = await info.context.dataloaders["category_by_id"].load(int(self.category_id))
        return api.category.Category.from_db(category)

    @strawberry.field
    async def payees(self, info: Info) \
            -> List[Annotated["Payee", strawberry.lazy("api.payee")]]:
        payees = await info.context.dataloaders["payees_by_subcategory_id"].load(int(self.id))
        return [Payee.marshal(p) for p in payees]

    @staticmethod
    def from_db(obj: db.schema.Subcategory) -> "Subcategory":
        return Subcategory(
            id=strawberry.ID(str(obj.id)),
            name=obj.name,
            category_id=obj.category_id
        )

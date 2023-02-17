from typing import TYPE_CHECKING, Annotated, List
import strawberry
from strawberry.types.info import Info
import db.schema
import api

if TYPE_CHECKING:
    from api.subcategory import Subcategory


@strawberry.type
class Category:
    id: strawberry.ID
    name: str
    is_expense: bool
    order: int
    exclude_from_reports: bool

    @strawberry.field
    async def subcategories(self, info: Info) \
            -> List[Annotated["Subcategory", strawberry.lazy("api.subcategory")]]:
        subcategories = await info.context.dataloaders["subcategories_by_category_id"].load(self.id)
        return [api.subcategory.Subcategory.from_db(s) for s in subcategories]

    @staticmethod
    def from_db(obj: db.schema.Category) -> "Category":
        return Category(
            id=strawberry.ID(str(obj.id)),
            name=obj.name,
            is_expense=obj.is_expense,
            order=obj.order,
            exclude_from_reports=obj.exclude_from_reports
        )

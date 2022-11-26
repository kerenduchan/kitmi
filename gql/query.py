import strawberry.types
import typing
import gql.schema
import db.schema
import db.session
import db.ops


async def _get_all(class_name, order_by_column_name):
    recs = await db.ops.get_all(class_name, order_by_column_name)
    gql_schema_class = getattr(gql.schema, class_name)
    return [gql_schema_class.marshal(r) for r in recs]


async def _get_one_by_id(class_name, id_):
    rec = await db.ops.get_one_by_id(class_name, id_)
    gql_schema_class = getattr(gql.schema, class_name)
    return gql_schema_class.marshal(rec)


@strawberry.type
class Query:

    @strawberry.field
    async def accounts(self) -> typing.List[gql.schema.Account]:
        return await _get_all("Account", "name")

    @strawberry.field
    async def categories(self) -> typing.List[gql.schema.Category]:
        return await _get_all("Category", "name")

    @strawberry.field
    async def subcategories(self) -> typing.List[gql.schema.Subcategory]:
        return await _get_all("Subcategory", "name")

    @strawberry.field
    async def payees(self) -> typing.List[gql.schema.Payee]:
        return await _get_all("Payee", "name")

    @strawberry.field
    async def transactions(self) -> typing.List[gql.schema.Transaction]:
        return await _get_all("Transaction", "date")

    @strawberry.field
    async def account(self, id: strawberry.ID) -> typing.Optional[gql.schema.Account]:
        return await _get_one_by_id("Account", id)

    @strawberry.field
    async def category(self, id: strawberry.ID) -> typing.Optional[gql.schema.Category]:
        return await _get_one_by_id("Category", id)

    @strawberry.field
    async def subcategory(self, id: strawberry.ID) -> typing.Optional[gql.schema.Subcategory]:
        return await _get_one_by_id("Subcategory", id)

    @strawberry.field
    async def payee(self, id: strawberry.ID) -> typing.Optional[gql.schema.Payee]:
        return await _get_one_by_id("Payee", id)

    @strawberry.field
    async def transaction(self, id: strawberry.ID) -> typing.Optional[gql.schema.Transaction]:
        return await _get_one_by_id("Transaction", id)

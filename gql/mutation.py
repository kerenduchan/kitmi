import typing
import datetime
import strawberry.types
import gql.schema
import db.schema
import db.session
import db.ops


@strawberry.type
class Mutation:

    @strawberry.mutation
    async def create_account(self, name: str, source: gql.schema.AccountSource,
                             username: str, password: str) \
            -> typing.Optional[gql.schema.Account]:

        async with db.session.get_session() as s:
            rec = await db.ops.create_account(s, name, source.value, username, password)
        return gql.schema.Account.marshal(rec)

    @strawberry.mutation
    async def create_category(self, name: str) \
            -> typing.Optional[gql.schema.Category]:
        async with db.session.get_session() as s:
            rec = await db.ops.create_category(s, name)
        return gql.schema.Category.marshal(rec)

    @strawberry.mutation
    async def create_subcategory(self, name: str, category_id: strawberry.ID) \
            -> typing.Optional[gql.schema.Subcategory]:
        async with db.session.get_session() as s:
            rec = await db.ops.create_subcategory(s, name, category_id)
        return gql.schema.Subcategory.marshal(rec)

    @strawberry.mutation
    async def create_payee(self, name: str, subcategory_id: typing.Optional[strawberry.ID]) \
            -> typing.Optional[gql.schema.Payee]:
        async with db.session.get_session() as s:
            rec = await db.ops.create_payee(s, name, subcategory_id)
        return gql.schema.Payee.marshal(rec)

    @strawberry.mutation
    async def create_transaction(self, date: datetime.date, amount: float,
                                 account_id: strawberry.ID,
                                 payee_id: strawberry.ID,
                                 subcategory_id: typing.Optional[strawberry.ID]) \
            -> gql.schema.Transaction:
        async with db.session.get_session() as s:
            rec = await db.ops.create_transaction(date,
                                                  amount,
                                                  account_id,
                                                  payee_id,
                                                  subcategory_id)
        return gql.schema.Transaction.marshal(rec)

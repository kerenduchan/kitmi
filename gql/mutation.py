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

        async with db.session.SessionMaker() as s:
            rec = await db.ops.create_account(s, name, source.value, username, password)
        return gql.schema.Account.marshal(rec)

    @strawberry.mutation
    async def create_category(self, name: str, is_expense: bool) \
            -> typing.Optional[gql.schema.Category]:
        async with db.session.SessionMaker() as s:
            rec = await db.ops.create_category(s, name, is_expense)
        return gql.schema.Category.marshal(rec)

    @strawberry.mutation
    async def rename_category(self, category_id: strawberry.ID, name: str) \
            -> typing.Optional[gql.schema.Category]:
        async with db.session.SessionMaker() as s:
            rec = await db.ops.rename_category(s, int(category_id), name)
        if rec is None:
            return None
        return gql.schema.Category.marshal(rec)

    @strawberry.mutation
    async def delete_category(self, category_id: strawberry.ID) \
            -> None:
        async with db.session.SessionMaker() as s:
            rec = await db.ops.delete_category(s, int(category_id))

    @strawberry.mutation
    async def create_subcategory(self, name: str, category_id: strawberry.ID) \
            -> typing.Optional[gql.schema.Subcategory]:
        async with db.session.SessionMaker() as s:
            rec = await db.ops.create_subcategory(s, name, category_id)
        return gql.schema.Subcategory.marshal(rec)

    @strawberry.mutation
    async def rename_subcategory(self, subcategory_id: strawberry.ID, name: str) \
            -> typing.Optional[gql.schema.Subcategory]:
        async with db.session.SessionMaker() as s:
            rec = await db.ops.rename_subcategory(s, int(subcategory_id), name)
        if rec is None:
            return None
        return gql.schema.Subcategory.marshal(rec)

    @strawberry.mutation
    async def delete_subcategory(self, subcategory_id: strawberry.ID) \
            -> None:
        async with db.session.SessionMaker() as s:
            rec = await db.ops.delete_subcategory(s, int(subcategory_id))

    @strawberry.mutation
    async def create_payee(self, name: str,
                           subcategory_id: typing.Optional[strawberry.ID],
                           note: str) \
            -> typing.Optional[gql.schema.Payee]:
        async with db.session.SessionMaker() as s:
            rec = await db.ops.create_payee(s, name, subcategory_id, note)
        return gql.schema.Payee.marshal(rec)

    @strawberry.mutation
    async def create_transaction(self, date: datetime.date, amount: float,
                                 account_id: strawberry.ID,
                                 payee_id: strawberry.ID,
                                 subcategory_id: typing.Optional[strawberry.ID],
                                 note: str) \
            -> gql.schema.Transaction:
        async with db.session.SessionMaker() as s:
            rec = await db.ops.create_transaction(s,
                                                  date,
                                                  amount,
                                                  account_id,
                                                  payee_id,
                                                  subcategory_id,
                                                  note)
        return gql.schema.Transaction.marshal(rec)

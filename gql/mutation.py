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
    async def update_account(self, account_id: strawberry.ID, name: str) \
            -> typing.Optional[gql.schema.Account]:
        async with db.session.SessionMaker() as s:
            rec = await db.ops.update_account(s, int(account_id), name)
        if rec is None:
            return None
        return gql.schema.Account.marshal(rec)

    @strawberry.mutation
    async def create_category(self, name: str, is_expense: bool) \
            -> typing.Optional[gql.schema.Category]:
        async with db.session.SessionMaker() as s:
            rec = await db.ops.create_category(s, name, is_expense)
        return gql.schema.Category.marshal(rec)

    @strawberry.mutation
    async def update_category(self, category_id: strawberry.ID, name: str, is_expense: bool) \
            -> typing.Optional[gql.schema.Category]:
        async with db.session.SessionMaker() as s:
            rec = await db.ops.update_category(s, int(category_id), name, is_expense)
        if rec is None:
            return None
        return gql.schema.Category.marshal(rec)

    @strawberry.mutation
    async def delete_category(self, category_id: strawberry.ID) \
            -> None:
        async with db.session.SessionMaker() as s:
            rec = await db.ops.delete_category(s, int(category_id))

    @strawberry.mutation
    async def move_category_down(self, category_id: strawberry.ID) \
            -> None:
        async with db.session.SessionMaker() as s:
            await db.ops.move_category(s, int(category_id), True)

    @strawberry.mutation
    async def move_category_up(self, category_id: strawberry.ID) \
            -> None:
        async with db.session.SessionMaker() as s:
            await db.ops.move_category(s, int(category_id), False)

    @strawberry.mutation
    async def create_subcategory(self, name: str, category_id: strawberry.ID) \
            -> typing.Optional[gql.schema.Subcategory]:
        async with db.session.SessionMaker() as s:
            rec = await db.ops.create_subcategory(s, name, category_id)
        return gql.schema.Subcategory.marshal(rec)

    @strawberry.mutation
    async def update_subcategory(self, subcategory_id: strawberry.ID,
                                 name: str, category_id: strawberry.ID) \
            -> typing.Optional[gql.schema.Subcategory]:
        async with db.session.SessionMaker() as s:
            rec = await db.ops.update_subcategory(s, int(subcategory_id), name, category_id)
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
    async def update_payee_subcategory(self, payee_id: strawberry.ID,
                                       subcategory_id: strawberry.ID) \
            -> typing.Optional[gql.schema.Payee]:
        async with db.session.SessionMaker() as s:
            rec = await db.ops.update_payee_subcategory(s,
                                                        int(payee_id),
                                                        int(subcategory_id))
        if rec is None:
            return None
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

    @strawberry.mutation
    async def update_transaction_subcategory(self, transaction_id: strawberry.ID,
                                             subcategory_id: typing.Optional[strawberry.ID]) \
            -> typing.Optional[gql.schema.Transaction]:
        async with db.session.SessionMaker() as s:
            if subcategory_id is not None:
                subcategory_id = int(subcategory_id)
            rec = await db.ops.update_transaction_subcategory(s,
                                                              transaction_id,
                                                              subcategory_id)
        if rec is None:
            return None
        return gql.schema.Transaction.marshal(rec)

import typing
import enum
import datetime
import strawberry
import strawberry.types
import strawberry.fastapi
import db.schema


@strawberry.enum
class AccountSource(enum.Enum):
    MAX = "max"
    LEUMI = "leumi"


@strawberry.type
class Account:
    id: strawberry.ID
    name: str
    source: AccountSource
    username: str
    password: str

    @staticmethod
    def marshal(model: db.schema.Account) -> "Account":
        return Account(id=strawberry.ID(str(model.id)),
                       name=model.name,
                       source=model.source,
                       username=model.username,
                       password=model.password)

    @strawberry.field
    async def transactions(self, info: strawberry.types.Info) -> list["Transaction"]:
        transactions = await info.context["transactions_by_accounts_loader"].load(int(self.id))
        return [Transaction.marshal(s) for t in transactions]


@strawberry.type
class Category:
    id: strawberry.ID
    name: str

    @strawberry.field
    async def subcategories(self, info: strawberry.types.Info) -> list["Subcategory"]:
        subcategories = await info.context["subcategories_by_categories_loader"].load(int(self.id))
        return [Subcategory.marshal(s) for s in subcategories]

    @staticmethod
    def marshal(model: db.schema.Category) -> "Category":
        return Category(
            id=strawberry.ID(str(model.id)),
            name=model.name
        )


@strawberry.type
class Subcategory:
    id: strawberry.ID
    name: str
    category_id: strawberry.ID

    @strawberry.field
    async def category(self, info: strawberry.types.Info) -> "Category":
        category = await info.context["categories_loader"].load(int(self.category_id))
        return Category.marshal(category)

    @strawberry.field
    async def payees(self, info: strawberry.types.Info) -> list["Payee"]:
        payees = await info.context["payees_by_subcategories_loader"].load(int(self.id))
        return [Payee.marshal(p) for p in payees]

    @staticmethod
    def marshal(model: db.schema.Subcategory) -> "Subcategory":
        return Subcategory(
            id=strawberry.ID(str(model.id)),
            name=model.name,
            category_id=model.category_id
        )


@strawberry.type
class Payee:
    id: strawberry.ID
    name: str
    subcategory_id: typing.Optional[strawberry.ID]

    @strawberry.field
    async def subcategory(self, info: strawberry.types.Info) -> typing.Optional["Subcategory"]:
        if self.subcategory_id is None:
            return None
        subcategory = await info.context["subcategories_loader"].load(int(self.subcategory_id))
        return Subcategory.marshal(subcategory)

    @strawberry.field
    async def transactions(self, info: strawberry.types.Info) -> list["Transaction"]:
        transactions = await info.context["transactions_by_payees_loader"].load(int(self.id))
        return [Transaction.marshal(t) for t in transactions]

    @staticmethod
    def marshal(model: db.schema.Payee) -> "Payee":
        return Payee(
            id=strawberry.ID(str(model.id)),
            name=model.name,
            subcategory_id=model.subcategory_id
        )


@strawberry.type
class Transaction:
    id: strawberry.ID
    date: datetime.date
    amount: float
    account_id: strawberry.ID
    payee_id: strawberry.ID
    subcategory_id: typing.Optional[strawberry.ID]

    @strawberry.field
    async def payee(self, info: strawberry.types.Info) -> "Payee":
        payee = await info.context["payees_loader"].load(self.payee_id)
        return Payee.marshal(payee)

    @strawberry.field
    async def account(self, info: strawberry.types.Info) -> "Account":
        account = await info.context["accounts_loader"].load(self.account_id)
        return Account.marshal(account)

    @strawberry.field
    async def subcategory(self, info: strawberry.types.Info) -> typing.Optional["Subcategory"]:
        if self.subcategory_id is None:
            return None
        s = await info.context["subcategories_loader"].load(self.subcategory_id)
        return Subcategory.marshal(s)

    @staticmethod
    def marshal(model: db.schema.Transaction) -> "Transaction":
        return Transaction(
            id=strawberry.ID(str(model.id)),
            date=model.date,
            amount=model.amount,
            account_id=model.account_id,
            payee_id=model.payee_id,
            subcategory_id=model.subcategory_id
        )

import typing
import enum
import datetime
import strawberry
import strawberry.types
import strawberry.fastapi
import db.schema
import model.yearly_summary
import model.summary
import model.subcategory_usage_info


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
    def marshal(obj: db.schema.Account) -> "Account":
        return Account(id=strawberry.ID(str(obj.id)),
                       name=obj.name,
                       source=obj.source.value,
                       username=obj.username,
                       password=obj.password)

    @strawberry.field
    async def transactions(self, info: strawberry.types.Info) -> list["Transaction"]:
        transactions = await info.context["transactions_by_accounts_loader"].load(int(self.id))
        return [Transaction.marshal(t) for t in transactions]


@strawberry.type
class Category:
    id: strawberry.ID
    name: str
    is_expense: bool
    order: int
    exclude_from_reports: bool

    @strawberry.field
    async def subcategories(self, info: strawberry.types.Info) -> list["Subcategory"]:
        subcategories = await info.context["subcategories_by_categories_loader"].load(int(self.id))
        return [Subcategory.marshal(s) for s in subcategories]

    @staticmethod
    def marshal(obj: db.schema.Category) -> "Category":
        return Category(
            id=strawberry.ID(str(obj.id)),
            name=obj.name,
            is_expense=obj.is_expense,
            order=obj.order,
            exclude_from_reports=obj.exclude_from_reports
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
    def marshal(obj: db.schema.Subcategory) -> "Subcategory":
        return Subcategory(
            id=strawberry.ID(str(obj.id)),
            name=obj.name,
            category_id=obj.category_id
        )


@strawberry.type
class Payee:
    id: strawberry.ID
    name: str
    subcategory_id: typing.Optional[strawberry.ID]
    note: str

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
    def marshal(obj: db.schema.Payee) -> "Payee":
        return Payee(
            id=strawberry.ID(str(obj.id)),
            name=obj.name,
            subcategory_id=obj.subcategory_id,
            note=obj.note,
        )


@strawberry.type
class Transaction:
    id: strawberry.ID
    date: datetime.date
    amount: float
    account_id: strawberry.ID
    payee_id: strawberry.ID
    subcategory_id: typing.Optional[strawberry.ID]
    note: str

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
    def marshal(obj: db.schema.Transaction) -> "Transaction":
        return Transaction(
            id=strawberry.ID(str(obj.id)),
            date=obj.date,
            amount=obj.amount,
            account_id=obj.account_id,
            payee_id=obj.payee_id,
            subcategory_id=obj.subcategory_id,
            note=obj.note
        )


@strawberry.type
class YearlySummaryRow:
    subcategory_id: strawberry.ID
    monthly_sums: typing.List[float]
    total_sum: float

    @strawberry.field
    async def subcategory(self, info: strawberry.types.Info) -> typing.Optional["Subcategory"]:
        s = await info.context["subcategories_loader"].load(self.subcategory_id)
        return Subcategory.marshal(s)

    @staticmethod
    def marshal(obj: model.yearly_summary.YearlySummaryRow) -> "YearlySummaryRow":
        return YearlySummaryRow(
            subcategory_id=obj.subcategory_id,
            monthly_sums=obj.monthly_sums,
            total_sum=obj.total_sum
        )


@strawberry.type
class YearlySummary:
    year: int
    rows: typing.List[YearlySummaryRow]

    @staticmethod
    def marshal(obj: model.yearly_summary.YearlySummary) -> "YearlySummary":
        return YearlySummary(
            year=obj.year,
            rows=[YearlySummaryRow.marshal(row) for s_id, row in obj.rows.items()],
        )


@strawberry.type
class SummaryForOneGroup:
    group_id: strawberry.ID
    name: str
    data: typing.List[float]

    @staticmethod
    def marshal(obj: model.summary.SummaryForOneGroup) -> "SummaryForOneGroup":
        return SummaryForOneGroup(
            group_id=obj.group_id,
            name=obj.name,
            data=obj.data,
        )


@strawberry.type
class Summary:
    x_axis: typing.List[str]
    groups: typing.List[SummaryForOneGroup]

    @staticmethod
    def marshal(obj: model.summary.Summary) -> "Summary":
        return Summary(
            x_axis=obj.x_axis,
            groups=[SummaryForOneGroup.marshal(g) for g_id, g in obj.groups.items()],
        )


@strawberry.type
class SubcategoryUsageInfo:
    is_used: bool

    @staticmethod
    def marshal(obj: model.subcategory_usage_info.SubcategoryUsageInfo) -> "SubcategoryUsageInfo":
        return SubcategoryUsageInfo(
            is_used=obj.is_used
        )

import typing
import enum
import datetime
import strawberry
import strawberry.types
import strawberry.fastapi
import db.schema
import summarize.summary
import summarize.summary_for_one_group
import model.subcategory_usage_info
import summarize.balance_summary


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
    override_subcategory: bool
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
            override_subcategory=obj.override_subcategory,
            subcategory_id=obj.subcategory_id,
            note=obj.note
        )


@strawberry.type
class SummaryForOneGroup:
    group_id: strawberry.ID
    name: str
    data: typing.List[float]
    total: float

    @staticmethod
    def marshal(obj: summarize.summary_for_one_group.SummaryForOneGroup) -> "SummaryForOneGroup":
        return SummaryForOneGroup(
            group_id=obj.group_id,
            name=obj.name,
            data=obj.data,
            total=obj.total
        )


@strawberry.type
class Summary:
    buckets: typing.List[str]
    groups: typing.List[SummaryForOneGroup]
    bucket_totals: typing.List[float]
    sum_total: float

    @staticmethod
    def marshal(obj: summarize.summary.Summary) -> "Summary":
        return Summary(
            buckets=obj.buckets,
            groups=[SummaryForOneGroup.marshal(g) for g_id, g in obj.groups.items()],
            bucket_totals=obj.bucket_totals,
            sum_total=obj.sum_total
        )


@strawberry.enum
class SummaryGroupBy(enum.Enum):
    category = "category"
    subcategory = "subcategory"


@strawberry.enum
class SummaryBucketBy(enum.Enum):
    month = "month"
    range = "range"


@strawberry.type
class BalanceSummary:
    income: Summary
    expenses: Summary
    savings: typing.List[float]
    savings_total: float
    savings_percentages: typing.List[int]
    savings_total_percentage: int

    @staticmethod
    def marshal(obj: summarize.balance_summary.BalanceSummary) -> "BalanceSummary":
        return BalanceSummary(
            income=Summary.marshal(obj.income),
            expenses=Summary.marshal(obj.expenses),
            savings=obj.savings,
            savings_total=obj.savings_total,
            savings_percentages=obj.savings_percentages,
            savings_total_percentage=obj.savings_total_percentage
        )


@strawberry.input
class SummaryOptions:
    is_expense: bool
    group_by: SummaryGroupBy
    bucket_by: SummaryBucketBy
    merge_under_threshold: bool

    def convert(self):
        return summarize.options.SummaryOptions(
            is_expense=self.is_expense,
            group_by=self.group_by,
            bucket_by=self.bucket_by,
            merge_under_threshold=self.merge_under_threshold
        )


@strawberry.type
class SubcategoryUsageInfo:
    is_used: bool

    @staticmethod
    def marshal(obj: model.subcategory_usage_info.SubcategoryUsageInfo) -> "SubcategoryUsageInfo":
        return SubcategoryUsageInfo(
            is_used=obj.is_used
        )

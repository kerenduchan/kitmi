from typing import TypeVar, List
from datetime import date
from api.pagination_window import PaginationWindow
from api.account import Account
from api.category import Category
from api.subcategory import Subcategory
from api.transaction import Transaction
from api.transactions_filter import TransactionsFilter
from api.summary import Summary
from api.balance_summary import BalanceSummary
from api.summary_options import SummaryOptions, SummaryGroupBy
import db.globals
import db.utils
import db.transaction
import db.schema
from summarize.transactions_summarizer import TransactionsSummarizer
from summarize.balance_summarizer import BalanceSummarizer
import summarize.options

ApiClass = TypeVar("ApiClass")


def get_resolver_fn(
        api_class: ApiClass,
        filter_class: type | None,
        db_class: type,
        default_order_by: str):

    async def resolve(
            order_by: str | None = default_order_by,
            filter: filter_class | None = None,
            limit: int = None,
            offset: int = 0) -> PaginationWindow[api_class]:

        db_filter = None if filter is None else filter.to_db_filter()

        async with db.globals.session_maker() as session:
            window = await db.utils.get(
                session, db_class, order_by, db_filter, limit, offset)

            return PaginationWindow[api_class](
                items=[api_class.from_db(item) for item in window.items],
                total_items_count=window.total_items_count)

    return resolve


async def get_transactions(
        order_by: str | None = "date",
        filter: TransactionsFilter | None = None,
        limit: int = None,
        offset: int = 0) -> PaginationWindow[Transaction]:
    db_filter = None if filter is None else filter.to_db_filter()

    async with db.globals.session_maker() as session:
        window = await db.transaction.get_transactions(
            session, order_by, db_filter, limit, offset)

        return PaginationWindow[Transaction](
            items=[Transaction.from_db(item) for item in window.items],
            total_items_count=window.total_items_count)


async def get_all_accounts(order_by: str | None = "name") -> List[Account]:
    async with db.globals.session_maker() as session:
        recs = await db.utils.get_all(session, db.schema.Account, order_by)
        return [Account.from_db(rec) for rec in recs]


async def get_all_categories(order_by: str | None = "order") -> List[Category]:
    async with db.globals.session_maker() as session:
        recs = await db.utils.get_all(session, db.schema.Category, order_by)
        return [Category.from_db(rec) for rec in recs]


async def get_all_subcategories(order_by: str | None = "name") -> List[Subcategory]:
    async with db.globals.session_maker() as session:
        recs = await db.utils.get_all(session, db.schema.Subcategory, order_by)
        return [Subcategory.from_db(rec) for rec in recs]


async def summary(
        start_date: date,
        end_date: date,
        options: SummaryOptions) -> Summary:
    summarizer = TransactionsSummarizer()
    async with db.globals.session_maker() as session:
        res = await summarizer.execute(
            session,
            start_date,
            end_date,
            options.convert())
    return Summary.from_db(res)


async def balance_summary(start_date: date,
                          end_date: date,
                          group_by: SummaryGroupBy) -> BalanceSummary:
    summarizer = BalanceSummarizer()
    async with db.globals.session_maker() as session:
        res = await summarizer.execute(
            session,
            start_date,
            end_date,
            summarize.options.SummaryGroupBy(group_by.value))
    return BalanceSummary.from_db(res)

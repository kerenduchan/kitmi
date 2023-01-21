from typing import TypeVar, List
from datetime import date
from api.pagination_window import PaginationWindow
from api.account import Account
from api.category import Category
from api.subcategory import Subcategory
from api.summary import Summary
from api.balance_summary import BalanceSummary
from api.summary_options import SummaryOptions, SummaryGroupBy
from db.session import session_maker
import db.utils
import db.account
import db.schema
from summarize.transactions_summarizer import TransactionsSummarizer
from summarize.balance_summarizer import BalanceSummarizer
import summarize.options

DEFAULT_LIMIT = 100
ApiClass = TypeVar("ApiClass")


def get_resolver_fn(
        api_class: ApiClass,
        filter_class: type | None,
        db_class: type,
        default_order_by: str):

    async def resolve(
            order_by: str | None = default_order_by,
            filter: filter_class | None = None,
            limit: int = DEFAULT_LIMIT,
            offset: int = 0) -> PaginationWindow[api_class]:

        db_filter = None if filter is None else filter.to_db_filter()

        async with session_maker() as session:
            window = await db.utils.get(
                session, db_class, order_by, db_filter, limit, offset)

            return PaginationWindow[api_class](
                items=[api_class.from_db(item) for item in window.items],
                total_items_count=window.total_items_count)

    return resolve


def get_resolver_fn_no_filter(
        api_class: ApiClass,
        db_class: type,
        default_order_by: str):

    async def resolve(
            order_by: str | None = default_order_by,
            limit: int = DEFAULT_LIMIT,
            offset: int = 0) -> PaginationWindow[api_class]:

        async with session_maker() as session:
            window = await db.utils.get(
                session, db_class, order_by, None, limit, offset)

            return PaginationWindow[api_class](
                items=[api_class.from_db(item) for item in window.items],
                total_items_count=window.total_items_count)

    return resolve


async def get_all_accounts(order_by: str | None = "name") -> List[Account]:
    async with session_maker() as session:
        recs = await db.account.get_all_accounts(session, order_by)
        return [Account.from_db(rec) for rec in recs]


async def get_all_categories(order_by: str | None = "order") -> List[Category]:
    async with session_maker() as session:
        recs = await db.utils.get_all(session, db.schema.Category, order_by)
        return [Category.from_db(rec) for rec in recs]


async def get_all_subcategories(order_by: str | None = "name") -> List[Subcategory]:
    async with session_maker() as session:
        recs = await db.utils.get_all(session, db.schema.Subcategory, order_by)
        return [Subcategory.from_db(rec) for rec in recs]


async def summary(
        start_date: date,
        end_date: date,
        options: SummaryOptions) -> Summary:
    summarizer = TransactionsSummarizer()
    async with session_maker() as session:
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
    async with session_maker() as session:
        res = await summarizer.execute(
            session,
            start_date,
            end_date,
            summarize.options.SummaryGroupBy(group_by.value))
    return BalanceSummary.from_db(res)

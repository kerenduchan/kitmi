from typing import List
import strawberry
from api.pagination_window import PaginationWindow
from api.query_resolvers import get_transactions, get_resolver_fn, get_all_accounts, \
    summary, balance_summary, get_all_categories, get_all_subcategories
from api.category import Category
from api.subcategory import Subcategory
from api.payee import Payee
from api.transaction import Transaction
from api.payees_filter import PayeesFilter
from api.account import Account
from api.summary import Summary
from api.balance_summary import BalanceSummary
import db.schema


@strawberry.type
class Query:

    accounts: List[Account] = strawberry.field(
        resolver=get_all_accounts,
        description="get all accounts")

    categories: List[Category] = strawberry.field(
        resolver=get_all_categories,
        description="get all categories")

    subcategories: List[Subcategory] = strawberry.field(
        resolver=get_all_subcategories,
        description="get all subcategories")

    payees: PaginationWindow[Payee] = strawberry.field(
        resolver=get_resolver_fn(Payee, PayeesFilter, db.schema.Payee, "name"),
        description="get payees")

    transactions: PaginationWindow[Transaction] = strawberry.field(
        resolver=get_transactions,
        description="get transactions")

    summary: Summary = strawberry.field(
        resolver=summary,
        description="get summary")

    balance_summary: BalanceSummary = strawberry.field(
        resolver=balance_summary,
        description="get balance summary")

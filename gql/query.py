import strawberry.types
import typing
import datetime
import gql.schema
import db.schema
import db.session
import db.ops
import summarize.transactions_summarizer
import summarize.balance_summarizer
import summarize.options


async def _begin_session_and_get_all(class_name, order_by_column_name):
    async with db.session.SessionMaker() as session:
        recs = await db.ops.get_all(session, class_name, order_by_column_name)
    gql_schema_class = getattr(gql.schema, class_name)
    return [gql_schema_class.marshal(r) for r in recs]


async def _begin_session_and_get_one_by_id(class_name, id_):
    async with db.session.SessionMaker() as session:
        rec = await db.ops.get_one_by_id(session, class_name, id_)
    gql_schema_class = getattr(gql.schema, class_name)
    return gql_schema_class.marshal(rec)


DEFAULT_PAGE_SIZE = 20


async def _get_page(class_name: str, order_by: str,
                    page_number: int = 1,
                    page_size: int = DEFAULT_PAGE_SIZE) \
        -> gql.schema.Page[gql.schema.GenericType]:
    """ return a page of items of the given class_name """
    async with db.session.SessionMaker() as session:

        if page_size == 0:
            # get all items in one page
            recs = await db.ops.get_all(session, class_name, order_by)
            gql_schema_class = getattr(gql.schema, class_name)
            items = [gql_schema_class.marshal(r) for r in recs]
            return gql.schema.Page(pages_count=1, items=items)

        if page_size < 0:
            raise Exception(f'page size ({page_size}) must be >= 0')

        # count how many pages there are in total
        pages_count = await db.ops.count_pages(
            session, class_name, page_size)

        if pages_count == 0:
            # there are no items of the given class_name in the db
            return gql.schema.Page(pages_count=0, items=[])

        if not 1 <= page_number <= pages_count:
            raise Exception(f'page number ({page_number}) '
                            f'is out of range (1-{pages_count})')

        offset = (page_number - 1) * page_size

        # get one extra item, to check if there is a next page
        page_from_db = await db.ops.get_page(
            session, class_name, order_by, page_size + 1, offset)

        # determine whether there is a next page
        has_next_page = len(page_from_db) == page_size + 1

        # Erase the extra book, if there was one.
        if has_next_page:
            page_from_db = page_from_db[:-1]

        return gql.schema.Page(pages_count=pages_count, items=page_from_db)


@strawberry.type
class Query:

    @strawberry.field
    async def accounts(self) -> typing.List[gql.schema.Account]:
        async with db.session.SessionMaker() as session:
            recs = await db.ops.get_all_accounts(session)
        return [gql.schema.Account.marshal(r) for r in recs]

    @strawberry.field
    async def categories(self) -> typing.List[gql.schema.Category]:
        return await _begin_session_and_get_all("Category", "order")

    @strawberry.field
    async def subcategories(self) -> typing.List[gql.schema.Subcategory]:
        return await _begin_session_and_get_all("Subcategory", "name")

    @strawberry.field
    async def payees(self) -> typing.List[gql.schema.Payee]:
        return await _begin_session_and_get_all("Payee", "name")

    @strawberry.field
    async def transactions(
            self, order_by: str = 'date',
            page_number: int = 1,
            page_size: int = DEFAULT_PAGE_SIZE) \
            -> gql.schema.Page[gql.schema.Transaction]:
        return await _get_page('Transaction', order_by, page_number, page_size)

    @strawberry.field
    async def account(self, id: strawberry.ID) -> typing.Optional[gql.schema.Account]:
        async with db.session.SessionMaker() as session:
            rec = await db.ops.get_account_by_id(session, int(id))
        return gql.schema.Account.marshal(rec)

    @strawberry.field
    async def category(self, id: strawberry.ID) -> typing.Optional[gql.schema.Category]:
        return await _begin_session_and_get_one_by_id("Category", id)

    @strawberry.field
    async def subcategory(self, id: strawberry.ID) -> typing.Optional[gql.schema.Subcategory]:
        return await _begin_session_and_get_one_by_id("Subcategory", id)

    @strawberry.field
    async def payee(self, id: strawberry.ID) -> typing.Optional[gql.schema.Payee]:
        return await _begin_session_and_get_one_by_id("Payee", id)

    @strawberry.field
    async def transaction(self, id: strawberry.ID) -> typing.Optional[gql.schema.Transaction]:
        return await _begin_session_and_get_one_by_id("Transaction", id)

    @strawberry.field
    async def summary(self, start_date: datetime.date,
                      end_date: datetime.date, options: gql.schema.SummaryOptions)\
            -> typing.Optional[gql.schema.Summary]:
        summarizer = summarize.transactions_summarizer.TransactionsSummarizer()
        async with db.session.SessionMaker() as session:
            res = await summarizer.execute(
                session,
                start_date,
                end_date,
                options.convert())
        return gql.schema.Summary.marshal(res)

    @strawberry.field
    async def balance_summary(self, start_date: datetime.date,
                              end_date: datetime.date,
                              group_by: gql.schema.SummaryGroupBy) \
            -> typing.Optional[gql.schema.BalanceSummary]:
        summarizer = summarize.balance_summarizer.BalanceSummarizer()
        async with db.session.SessionMaker() as session:
            res = await summarizer.execute(
                session,
                start_date,
                end_date,
                summarize.options.SummaryGroupBy(group_by.value))
        return gql.schema.BalanceSummary.marshal(res)

    @strawberry.field
    async def subcategory_usage_info(self, subcategory_id: strawberry.ID) -> \
            typing.Optional[gql.schema.SubcategoryUsageInfo]:
        async with db.session.SessionMaker() as session:
            res = await db.ops.get_subcategory_usage_info(session, subcategory_id)
        return gql.schema.SubcategoryUsageInfo.marshal(res)

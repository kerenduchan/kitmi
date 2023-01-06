import summarize.i_summary_source
import summarize.summary_source_item
import sqlalchemy
import db.schema
import util


class TransactionsSource(summarize.i_summary_source.ISummarySource):
    """ Concrete class - the summary source for transactions """

    def __init__(self, session, is_expense, start_date, end_date, group_by):
        assert group_by in ['category', 'subcategory']
        self._session = session
        self._is_expense = is_expense
        self._start_date = start_date
        self._end_date = end_date
        self._group_by = group_by

        self._buckets = util.get_months(start_date, end_date)
        self._bucket_name_to_bucket_idx = {bucket: idx for idx, bucket in enumerate(self._buckets)}

        # will be filled by the load() function
        self._items = []

        # dict of category_id => category_name for each category that should be
        # included in the summary, ordered by category order
        self._category_id_to_name = {}

        # dict of subcategory_id => subcategory_name for each subcategory that
        # should be included in the summary, ordered by category order
        self._subcategory_id_to_name = {}

        # dict of subcategory_id => category_id for each subcategory that
        # should be included in the summary
        self._subcategory_id_to_category_id = {}

    async def load(self):

        # init _category_id_to_name
        await self._load_categories()

        # init _subcategory_id_to_name and _subcategory_id_to_category_id
        await self._load_subcategories()

        # get transactions data from the db (includes the payee's subcategory_id)
        transactions_data = \
            await self._load_transactions_data(
                self._session,
                self._start_date,
                self._end_date)

        # init _items
        self._fill_items(transactions_data)

    def get_groups(self):
        if self._group_by == 'category':
            return self._category_id_to_name

        return self._subcategory_id_to_name

    def get_buckets(self):
        return self._buckets

    def get_items(self):
        return self._items

    async def _load_categories(self):
        # Get all expense/income categories (depending on is_expense)
        # that are not 'excluded from reports'
        sql = sqlalchemy.select(db.schema.Category) \
            .where(db.schema.Category.is_expense == self._is_expense) \
            .where(db.schema.Category.exclude_from_reports == False) \
            .order_by(db.schema.Category.order)
        categories = (await self._session.execute(sql)).scalars().unique().all()

        # map these categories: id => name
        self._category_id_to_name = {c.id: c.name for c in categories}

    async def _load_subcategories(self):
        # Get all subcategories that belong to the given categories
        sql = sqlalchemy.select(db.schema.Subcategory)
        all_subcategories = (await self._session.execute(sql)).scalars().unique().all()

        # The following allows ordering subcategories by the categories' order
        # and filtering only the subcategories that belong to the given
        # categories
        category_id_to_subcategories = \
            {c_id: [] for c_id, c_name in self._category_id_to_name.items()}
        for s in all_subcategories:
            found = category_id_to_subcategories.get(s.category_id)
            if found is not None:
                found.append(s)

        # map these subcategories: id => name and id => category_id
        self._subcategory_id_to_name = {}
        for c_id, subcategories in category_id_to_subcategories.items():
            for s in subcategories:
                self._subcategory_id_to_name[s.id] = s.name
                self._subcategory_id_to_category_id[s.id] = s.category_id

    @staticmethod
    async def _load_transactions_data(session, start_date, end_date):
        # get transaction amount, date, subcategory_id, payees.subcategory_id
        # for all transactions whose date is between start_date and end_date
        sql = sqlalchemy.select(
            db.schema.Transaction.amount,
            db.schema.Transaction.date,
            db.schema.Transaction.subcategory_id,
            db.schema.Payee.subcategory_id) \
            .join_from(db.schema.Transaction,
                       db.schema.Payee) \
            .filter(db.schema.Transaction.date >= start_date) \
            .filter(db.schema.Transaction.date <= end_date)
        return (await session.execute(sql)).all()

    def _fill_items(self, transactions_data):
        """ Fill _items with transactions that are included in the summary """

        for td in transactions_data:
            (amount, date, transaction_subcategory_id, payee_subcategory_id) \
                = td

            # Determine the actual subcategory_id for the transaction
            # (either of the payee or of the transaction)
            subcategory_id = transaction_subcategory_id
            if subcategory_id is None:
                subcategory_id = payee_subcategory_id

            # Determine the category_id for the transaction
            category_id = self._subcategory_id_to_category_id.get(subcategory_id)

            # add the transaction to the list only if its category is not
            # filtered out
            if category_id is not None:

                # the group_id of this item
                group_id = category_id
                if self._group_by == 'subcategory':
                    group_id = subcategory_id

                item = summarize.summary_source_item.SummarySourceItem(
                    value=amount,
                    bucket_idx=self._get_bucket_idx(date),
                    group_id=group_id)
                self._items.append(item)

    def _get_bucket_idx(self, date):
        month_and_year = date.strftime('%Y-%m')
        return self._bucket_name_to_bucket_idx[month_and_year]

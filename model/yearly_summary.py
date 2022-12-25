import typing


class YearlySummaryRow:
    subcategory_id: int
    monthly_sums: typing.List[int]
    total_sum: int

    def __init__(self, subcategory_id):
        self.subcategory_id = subcategory_id
        self.monthly_sums = [0 for i in range(12)]
        self.total_sum = 0


class YearlySummary:
    year: int
    rows: typing.Dict[int, YearlySummaryRow]

    def __init__(self, year):
        self.year = year
        self.rows = {}

    def add_subcategory(self, subcategory_id):
        self.rows[subcategory_id] = YearlySummaryRow(subcategory_id)

    def add_transactions(self, transactions, payees):
        # map of payee_id => subcategory_id
        payee_id_to_subcategory_id = {p.id: p.subcategory_id for p in payees}

        for t in transactions:
            self._add_transaction(t, payee_id_to_subcategory_id)

    def _add_transaction(self, transaction, payee_id_to_subcategory_id):

        # determine the subcategory of the transaction
        subcategory_id = transaction.subcategory_id
        if subcategory_id is None:
            # fall back to the subcategory of this transaction's payee
            subcategory_id = payee_id_to_subcategory_id[transaction.payee_id]

        if subcategory_id is None:
            # this transaction is uncategorized
            return

        # add this transaction's amount to the sum for this subcategory
        row = self.rows[subcategory_id]
        row.total_sum += transaction.amount

        month = transaction.date.month - 1
        row.monthly_sums[month] += transaction.amount


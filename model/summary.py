import typing
import enum


# summary for one category or for one subcategory
class SummaryForOneGroup:
    group_id: int
    monthly_sums: typing.List[int]
    total_sum: int

    def __init__(self, group_id, group_name):
        self.group_id = group_id
        self.group_name = group_name
        self.monthly_sums = [0 for i in range(12)]
        self.total_sum = 0


class Summary:

    groups: typing.Dict[int, SummaryForOneGroup]
    x_axis: typing.List[str]

    def __init__(self, group_by, payees, subcategories=None):

        # group_by should be "category" or "subcategory"
        self.group_by = group_by

        self.groups = {}
        self.x_axis = ['02/2022', '03/2022', '04/2022', '05/2022', '06/2022']

        # Map of payee_id => subcategory_id
        self._payee_id_to_subcategory_id = {p.id: p.subcategory_id for p in payees}

        # Map of subcategory_id => category_id
        # Needed only if grouping by category
        self._subcategory_id_to_category_id = None
        if self.group_by == "category":
            subcategory_id_to_category_id = \
                {s.id: s.category_id for s in subcategories}

    def add_group(self, group_id, group_name):
        self.groups[group_id] = SummaryForOneGroup(group_id, group_name)

    # Add the given transactions to the summary (in the correct group)
    # subcategories are needed if grouping by category
    def add_transactions(self, transactions):

        # Add each transaction to the summary (in the correct group)
        for t in transactions:
            self._add_transaction(t)

    def _add_transaction(self, transaction):

        # Determine the subcategory of the transaction
        subcategory_id = transaction.subcategory_id
        if subcategory_id is None:
            # Fall back to the subcategory of this transaction's payee
            subcategory_id = self._payee_id_to_subcategory_id[transaction.payee_id]

        if subcategory_id is None:
            # This transaction is uncategorized.
            # It won't appear in the summary.
            return

        # Determine the group_id
        group_id = subcategory_id
        if self.group_by == "category":
            group_id = self._subcategory_id_to_category_id[subcategory_id]

        # Add this transaction's amount to the sum for this group
        group = self.groups[group_id]
        group.total_sum += transaction.amount

        month = transaction.date.month - 1
        group.monthly_sums[month] += transaction.amount


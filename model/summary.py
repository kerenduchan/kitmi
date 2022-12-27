import typing
import util


# summary for one category or for one subcategory
class SummaryForOneGroup:
    group_id: int
    name: str
    data: typing.List[int]

    def __init__(self, group_id, name, months_count):
        self.group_id = group_id
        self.name = name
        self.data = [0 for i in range(months_count)]

    def is_empty(self):
        for d in self.data:
            if d != 0:
                return False
        return True


class Summary:

    groups: typing.Dict[int, SummaryForOneGroup]
    x_axis: typing.List[str]

    def __init__(self, start_date, end_date, group_by, is_reverse_sign, payees, subcategories=None):

        # group_by should be "category" or "subcategory"
        self.group_by = group_by

        self.is_reverse_sign = is_reverse_sign

        self.groups = {}

        self.x_axis = util.get_months(start_date, end_date)

        self._month_to_idx = {month: idx for idx, month in enumerate(self.x_axis)}

        # Map of payee_id => subcategory_id
        self._payee_id_to_subcategory_id = {p.id: p.subcategory_id for p in payees}

        # Map of subcategory_id => category_id
        # Needed only if grouping by category
        self._subcategory_id_to_category_id = None
        if self.group_by == "category":
            subcategory_id_to_category_id = \
                {s.id: s.category_id for s in subcategories}

    def add_group(self, group_id, group_name):
        self.groups[group_id] = SummaryForOneGroup(group_id, group_name, len(self.x_axis))

    # Add the given transactions to the summary (in the correct group)
    # subcategories are needed if grouping by category
    def add_transactions(self, transactions):

        # Add each transaction to the summary (in the correct group)
        for t in transactions:
            self._add_transaction(t)

        # erase groups that are all zeros
        non_empty_groups = {}
        for g_id, g in self.groups.items():
            if not g.is_empty():
                non_empty_groups[g_id] = g

        self.groups = non_empty_groups

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

        month_and_year = transaction.date.strftime('%Y-%m')
        idx = self._month_to_idx[month_and_year]
        amount = transaction.amount

        if self.is_reverse_sign:
            amount = -amount
        group.data[idx] += amount


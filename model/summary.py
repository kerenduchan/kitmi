import typing
import util
import model.summary_for_one_group


class Summary:

    groups: typing.Dict[int, model.summary_for_one_group.SummaryForOneGroup]
    x_axis: typing.List[str]

    def __init__(self, start_date, end_date, group_by, is_reverse_sign, payees, subcategories):

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

        self._subcategory_id_to_category_id = \
            {s.id: s.category_id for s in subcategories}

    def get_months_count(self):
        return len(self.x_axis)

    def add_group(self, group_id, group_name):
        self.groups[group_id] = model.summary_for_one_group.SummaryForOneGroup(
            group_id, group_name, self.get_months_count())

    # Add the given transactions to the summary (in the correct group)
    # subcategories are needed if grouping by category
    def add_transactions(self, transactions):

        # Add each transaction to the summary (in the correct group)
        for t in transactions:
            self._add_transaction(t)

        self._erase_empty_groups()

        # reverse signs
        if self.is_reverse_sign:
            for g_id, g in self.groups.items():
                g.reverse_sign()

        # fix precision
        for g_id, g in self.groups.items():
            g.fix_precision()

        # merge under threshold
        self._merge_under_threshold()

        # erase empty groups again (more empty groups might have been created
        # by merge_under_threshold)
        self._erase_empty_groups()

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

        category_id = self._subcategory_id_to_category_id.get(subcategory_id)
        if category_id is None:
            # The subcategory of this transaction doesn't appear in the given
            # subcategories list. It won't appear in the summary.
            return

        # Determine the group_id
        group_id = category_id if (self.group_by == "category") else subcategory_id

        # Determine the month_idx for the transaction
        month_and_year = transaction.date.strftime('%Y-%m')
        month_idx = self._month_to_idx[month_and_year]

        # Add this transaction's amount to the sum for this group at this month_idx
        group = self.get_group_by_id(group_id)
        group.add_to_datapoint(month_idx, transaction.amount)

    def get_group_by_id(self, group_id):
        return self.groups[group_id]

    def _erase_empty_groups(self):
        # erase groups that are all zeros
        non_empty_groups = {}
        for g_id, g in self.groups.items():
            if not g.is_empty():
                non_empty_groups[g_id] = g

        self.groups = non_empty_groups

    def _merge_under_threshold(self):
        months_count = self.get_months_count()

        # create a group for "Other"
        other = model.summary_for_one_group.SummaryForOneGroup(0, "Other", months_count)

        # for each month: _merge_under_threshold_for_month
        for month_id in range(months_count):
            self._merge_under_threshold_for_month(month_id, other)

        # add the "Other" group to the summary if it is not empty
        if not other.is_empty():
            self.groups[0] = other

    def _merge_under_threshold_for_month(self, month_id, other):

        # list of (group_id, data) for this month_id for all groups
        month_data = self._get_data_for_month(month_id)

        # sort by the data (amount)
        month_data.sort(key=lambda data: data[1])

        # threshold for this month for all groups
        threshold = self._get_threshold_for_month(month_id)

        # merge groups under threshold only if there is more than one to merge
        threshold_idx = self._find_threshold_idx(month_data, threshold)

        merged_sum = 0
        if threshold_idx > 0:
            for i in range(threshold_idx + 1):
                (group_id, datapoint) = month_data[i]
                merged_sum += datapoint
                self.groups[group_id].data[month_id] = 0

        other.data[month_id] = merged_sum

    def _get_data_for_month(self, month_id):
        return [(g_id, g.data[month_id]) for g_id, g in self.groups.items()]

    def _get_threshold_for_month(self, month_id):
        res = 0
        for g_id, g in self.groups.items():
            res += g.data[month_id]
        return int(res / 10)

    # return the first index in month_data where the sums up
    # until this index are below the given threshold.
    @staticmethod
    def _find_threshold_idx(month_data, threshold):
        partial_sum = 0
        idx = -1
        for group_id, data in month_data:
            partial_sum += data
            if partial_sum > threshold:
                return idx
            idx += 1
        return idx

    def __repr__(self):
        return str(self.x_axis) + '\n' + str(self.groups)

import typing
from summarize.summary_for_one_group import SummaryForOneGroup


class Summary:

    groups: typing.Dict[int, SummaryForOneGroup]
    buckets: typing.List[str]
    totals: typing.List[float]

    def __init__(self, buckets):
        self.groups = {}
        self.buckets = buckets
        self.totals = [0 for i in range(len(buckets) + 1)]

    def get_buckets_count(self):
        return len(self.buckets)

    def add_group(self, group_id, group_name):
        self.groups[group_id] = SummaryForOneGroup(
            group_id, group_name, self.get_buckets_count())

    def get_group_by_id(self, group_id):
        return self.groups[group_id]

    def add(self, group_id, bucket_idx, value):
        group = self.get_group_by_id(group_id)
        group.add(bucket_idx, value)

    def set(self, group_id, bucket_idx, value):
        group = self.get_group_by_id(group_id)
        group.set(bucket_idx, value)

    def get_data_for_bucket(self, bucket_id):
        return [(g_id, g.get(bucket_id)) for g_id, g in self.groups.items()]

    def __repr__(self):
        return str(self.buckets) + '\n' + str(self.groups)

    def get_transposed_str(self):
        res = ''
        for bucket_idx, bucket in enumerate(self.buckets):
            res += f'{bucket}: '
            for g_id, g in self.groups.items():
                res += f'{g.name}={g.get(bucket_idx)} '
            if bucket_idx < self.get_buckets_count() - 1:
                res += '\n'

        return res

import typing
from summarize.summary_for_one_group import SummaryForOneGroup
import summarize.i_summary_source


class Summary:

    groups: typing.Dict[int, SummaryForOneGroup]
    x_axis: typing.List[str]

    def __init__(self, buckets):
        self.groups = {}
        self.x_axis = buckets

    def get_buckets_count(self):
        return len(self.x_axis)

    def add_group(self, group_id, group_name):
        self.groups[group_id] = SummaryForOneGroup(
            group_id, group_name, self.get_buckets_count())

    def get_group_by_id(self, group_id):
        return self.groups[group_id]

    def add(self, group_id, bucket_idx, amount):
        group = self.get_group_by_id(group_id)
        group.add(bucket_idx, amount)

    def set(self, group_id, bucket_idx, amount):
        group = self.get_group_by_id(group_id)
        group.set(bucket_idx, amount)

    def get_data_for_bucket(self, bucket_id):
        return [(g_id, g.get(bucket_id)) for g_id, g in self.groups.items()]

    def __repr__(self):
        return str(self.x_axis) + '\n' + str(self.groups)

    def get_transposed_str(self):
        res = ''
        for bucket_idx, bucket in enumerate(self.x_axis):
            res += f'{bucket}: '
            for g_id, g in self.groups.items():
                res += f'{g.name}={g.get(bucket_idx)} '
            if bucket_idx < len(self.x_axis) - 1:
                res += '\n'

        return res

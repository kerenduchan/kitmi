import typing


# Summary for one group
class SummaryForOneGroup:

    # The ID of the group
    group_id: int

    # The name of the group
    name: str

    # The datapoints (sums) for this group.
    # List length is equal to the number of buckets
    data: typing.List[int]

    # constructor
    def __init__(self, group_id, name, buckets_count):
        self.group_id = group_id
        self.name = name
        self.data = [0 for i in range(buckets_count)]

    # return the datapoint for the given bucket_idx
    def get_datapoint(self, bucket_idx):
        return self.data[bucket_idx]

    def add_to_datapoint(self, bucket_idx, amount):
        assert 0 <= bucket_idx < len(self.data)
        self.data[bucket_idx] += amount

    def is_empty(self):
        for d in self.data:
            if d != 0:
                return False
        return True

    def fix_precision(self):
        for i in range(len(self.data)):
            self.data[i] = int(self.data[i])

    def reverse_sign(self):
        for i in range(len(self.data)):
            self.data[i] = -self.data[i]

    def __repr__(self):
        return f"group_id={self.group_id} name='{self.name}' " + str(self.data)
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
    def __init__(self, group_id: int, name: str, buckets_count: int):
        self.group_id = group_id
        self.name = name
        self.data = [0 for i in range(buckets_count)]

    # return the datapoint for the given bucket_idx
    def get(self, bucket_idx: int) -> int:
        return self.data[bucket_idx]

    def add(self, bucket_idx: int, amount: int) -> None:
        self.data[bucket_idx] += amount

    def set(self, bucket_idx: int, amount: int) -> None:
        self.data[bucket_idx] = amount

    def is_empty(self) -> bool:
        for d in self.data:
            if d != 0:
                return False
        return True

    def __repr__(self):
        return f"'{self.name}': " + str(self.data)

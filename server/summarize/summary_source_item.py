import dataclasses


@dataclasses.dataclass
class SummarySourceItem:
    group_id: int
    bucket_idx: int
    value: float

    def __init__(self, group_id, bucket_idx, value):
        self.group_id = group_id
        self.bucket_idx = bucket_idx
        self.value = value

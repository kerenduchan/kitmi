import dataclasses
import enum


@dataclasses.dataclass
class SummaryGroupBy(enum.Enum):
    category = "category"
    subcategory = "subcategory"


@dataclasses.dataclass
class SummaryBucketBy(enum.Enum):
    month = "month"
    range = "range"


@dataclasses.dataclass
class SummaryOptions:
    is_expense: bool
    group_by: SummaryGroupBy
    bucket_by: SummaryBucketBy
    merge_under_threshold: bool

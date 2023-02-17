from enum import Enum
import strawberry
import summarize.options


@strawberry.enum
class SummaryGroupBy(Enum):
    category = "category"
    subcategory = "subcategory"


@strawberry.enum
class SummaryBucketBy(Enum):
    month = "month"
    range = "range"


@strawberry.input
class SummaryOptions:
    is_expense: bool
    group_by: SummaryGroupBy
    bucket_by: SummaryBucketBy
    merge_under_threshold: bool

    def convert(self):
        return summarize.options.SummaryOptions(
            is_expense=self.is_expense,
            group_by=self.group_by,
            bucket_by=self.bucket_by,
            merge_under_threshold=self.merge_under_threshold
        )

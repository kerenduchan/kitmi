from typing import List
import strawberry
import summarize.summary
from api.summary_for_one_group import SummaryForOneGroup


@strawberry.type
class Summary:
    buckets: List[str]
    groups: List[SummaryForOneGroup]
    bucket_totals: List[float]
    sum_total: float

    @staticmethod
    def from_db(obj: summarize.summary.Summary) -> "Summary":
        return Summary(
            buckets=obj.buckets,
            groups=[SummaryForOneGroup.from_db(g) for g_id, g in obj.groups.items()],
            bucket_totals=obj.bucket_totals,
            sum_total=obj.sum_total
        )

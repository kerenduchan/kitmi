from typing import List
import strawberry
import summarize.summary_for_one_group


@strawberry.type
class SummaryForOneGroup:
    group_id: strawberry.ID
    name: str
    data: List[float]
    total: float

    @staticmethod
    def from_db(obj: summarize.summary_for_one_group.SummaryForOneGroup) -> "SummaryForOneGroup":
        return SummaryForOneGroup(
            group_id=obj.group_id,
            name=obj.name,
            data=obj.data,
            total=obj.total
        )

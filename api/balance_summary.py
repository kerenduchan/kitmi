from typing import List
import strawberry
from api.summary import Summary
import summarize.balance_summary


@strawberry.type
class BalanceSummary:
    income: Summary
    expenses: Summary
    savings: List[float]
    savings_total: float
    savings_percentages: List[int]
    savings_total_percentage: int

    @staticmethod
    def from_db(obj: summarize.balance_summary.BalanceSummary) -> "BalanceSummary":
        return BalanceSummary(
            income=Summary.marshal(obj.income),
            expenses=Summary.marshal(obj.expenses),
            savings=obj.savings,
            savings_total=obj.savings_total,
            savings_percentages=obj.savings_percentages,
            savings_total_percentage=obj.savings_total_percentage
        )

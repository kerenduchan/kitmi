import typing
import summarize.summary


class IncomeVsExpensesSummary:
    income: summarize.summary.Summary
    expenses: summarize.summary.Summary
    savings: typing.List[float]
    savings_percentages: typing.List[int]

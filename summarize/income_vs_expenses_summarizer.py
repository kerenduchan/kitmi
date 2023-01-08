import datetime
import summarize.income_vs_expenses_summary
import summarize.transactions_summarizer
import summarize.options


class IncomeVsExpensesSummarizer:

    async def execute(self, session,
                      start_date: datetime.date,
                      end_date: datetime.date,
                      group_by):

        summary = summarize.income_vs_expenses_summary.IncomeVsExpensesSummary()

        summarizer = summarize.transactions_summarizer.TransactionsSummarizer()

        options = summarize.options.SummaryOptions(
            is_expense=False,
            group_by=group_by,
            bucket_by=summarize.options.SummaryBucketBy.month,
            merge_under_threshold=False
        )

        # fill the income summary
        summary.income = await summarizer.execute(session, start_date, end_date, options)

        # fill the expenses summary
        options.is_expense = True
        summary.expenses = await summarizer.execute(session, start_date, end_date, options)

        summary.savings = []
        summary.savings_percentages = []

        return summary

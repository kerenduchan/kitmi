import datetime
import summarize.balance_summary
import summarize.transactions_summarizer
import summarize.options


class BalanceSummarizer:

    async def execute(self, session,
                      start_date: datetime.date,
                      end_date: datetime.date,
                      group_by):

        summary = summarize.balance_summary.BalanceSummary()

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

        # fill the savings and savings_percentages
        income_and_expenses = zip(summary.income.bucket_totals, summary.expenses.bucket_totals)
        summary.savings = []
        summary.savings_percentages = []

        for income, expense in income_and_expenses:
            saving = income - expense
            summary.savings.append(saving)
            summary.savings_percentages.append(int(100 * saving / income))

        return summary

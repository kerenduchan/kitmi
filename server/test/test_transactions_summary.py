import asyncio
import datetime
from db.init import init_db
import db.globals
import summarize.options
from summarize.transactions_summarizer import TransactionsSummarizer


async def test():

    init_db()

    summarizer = TransactionsSummarizer()
    start_date = datetime.date.fromisoformat('2022-01-01')
    end_date = datetime.date.fromisoformat('2022-03-20')

    options = summarize.options.SummaryOptions(
        is_expense=True,
        group_by=summarize.options.SummaryGroupBy.subcategory,
        bucket_by=summarize.options.SummaryBucketBy.range,
        merge_under_threshold=False
    )
    async with db.globals.session_maker() as session:
        summary = await summarizer.execute(session, start_date, end_date, options)

    print(summary.get_transposed_str())


if __name__ == "__main__":
    asyncio.run(test())

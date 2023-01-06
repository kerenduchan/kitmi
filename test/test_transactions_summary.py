import asyncio
import datetime
import db.session
import db.schema
import sqlalchemy
from summarize.transactions_summarizer import TransactionsSummarizer


async def test():
    summarizer = TransactionsSummarizer()
    start_date = datetime.date.fromisoformat('2022-01-01')
    end_date = datetime.date.fromisoformat('2022-02-20')
    group_by = 'subcategory'
    is_expense = True
    async with db.session.SessionMaker() as session:
        summary = await summarizer.execute(session, start_date, end_date, group_by, is_expense)

    print(summary.get_transposed_str())


if __name__ == "__main__":
    asyncio.run(test())

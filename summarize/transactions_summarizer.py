import datetime

import summarize.transactions_source
import summarize.summarizer
from summarize.postprocess.erase_empty_groups import EraseEmptyGroups
from summarize.postprocess.fix_precision import FixPrecision
from summarize.postprocess.reverse_sign import ReverseSign
from summarize.postprocess.merge_under_threshold import MergeUnderThreshold
from summarize.postprocess.calc_totals import CalcTotals
from summarize.postprocess.order_groups_by_size_in_first_bucket import OrderGroupsBySizeInFirstBucket
import summarize.options


class TransactionsSummarizer:

    @staticmethod
    async def execute(session,
                      start_date: datetime.date,
                      end_date: datetime.date,
                      options: summarize.options.SummaryOptions):

        # load source data
        source = summarize.transactions_source.TransactionsSource(
            session, start_date, end_date, options)
        await source.load()

        # summarize
        summarizer = summarize.summarizer.Summarizer()
        summary = summarizer.execute(source)

        # post-process
        postprocessors = [FixPrecision()]

        if options.is_expense:
            postprocessors.append(ReverseSign())

        if options.merge_under_threshold:
            postprocessors.append(MergeUnderThreshold())

        postprocessors.append(EraseEmptyGroups())
        postprocessors.append(CalcTotals())

        if options.bucket_by.name == 'range':
            postprocessors.append(OrderGroupsBySizeInFirstBucket())

        for p in postprocessors:
            p.execute(summary)

        return summary

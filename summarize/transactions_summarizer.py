from summarize.transactions_source import TransactionsSource
from summarize.summarizer import Summarizer
from summarize.postprocess.erase_empty_groups import EraseEmptyGroups
from summarize.postprocess.fix_precision import FixPrecision
from summarize.postprocess.reverse_sign import ReverseSign
from summarize.postprocess.merge_under_threshold import MergeUnderThreshold


class TransactionsSummarizer:

    @staticmethod
    async def execute(session, start_date, end_date, group_by, is_expense):

        # load source data
        source = TransactionsSource(
            session, is_expense, start_date, end_date, group_by)
        await source.load()

        # summarize
        summarizer = Summarizer()
        summary = summarizer.execute(source)

        # post-process
        postprocessors = [FixPrecision()]

        if is_expense:
            postprocessors.append(ReverseSign())

        postprocessors.append(MergeUnderThreshold())
        postprocessors.append(EraseEmptyGroups())

        for p in postprocessors:
            p.execute(summary)

        return summary

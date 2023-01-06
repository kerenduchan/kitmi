import datetime
from summarize.i_summary_source import ISummarySource
from summarize.summary_source_item import SummarySourceItem
from summarize.summarizer import Summarizer
from summarize.postprocess.fix_precision import FixPrecision
from summarize.postprocess.reverse_sign import ReverseSign
from summarize.postprocess.erase_empty_groups import EraseEmptyGroups
from summarize.postprocess.merge_under_threshold import MergeUnderThreshold


class MockSummarySource(ISummarySource):

    def __init__(self):
        self._items = None
        self._groups = None
        self._buckets = None

    def load(self) -> None:
        self._items = [
            SummarySourceItem(1, 0, -100.99),
            SummarySourceItem(1, 0, -50.20),
            SummarySourceItem(2, 0, -20.32),
            SummarySourceItem(2, 1, -1.3),
            SummarySourceItem(3, 0, -1000.66),
            SummarySourceItem(3, 1, -10.1),
            SummarySourceItem(1, 1, -1.1),
            SummarySourceItem(1, 1, -240.6),
        ]

        self._groups = {
            1: "One",
            2: "Two",
            3: "Three",
            4: "Four"
        }

        self._buckets = [
            'Bucket 1',
            'Bucket 2'
        ]

    def get_groups(self):
        return self._groups

    def get_buckets(self):
        return self._buckets

    def get_items(self):
        return self._items


def test_mock_summary():
    source = MockSummarySource()
    source.load()

    summarizer = Summarizer()

    summary = summarizer.execute(source)
    print(summary.get_transposed_str())

    postprocessors = [
        FixPrecision(),
        ReverseSign(),
        MergeUnderThreshold(),
        EraseEmptyGroups(),
    ]

    for p in postprocessors:
        print(type(p).__name__)
        p.execute(summary)
        print(summary.get_transposed_str())


if __name__ == "__main__":
    test_mock_summary()

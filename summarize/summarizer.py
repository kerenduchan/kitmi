import typing
from summarize.summary import Summary
from summarize.i_summary_source import ISummarySource
from summarize.postprocess.i_postprocessor import IPostprocessor


class Summarizer:
    """ Creates a summary, given a source and a list of postprocessors """

    @staticmethod
    def execute(source: ISummarySource) -> Summary:

        # Create the result summary object.
        summary = Summary(source.get_buckets())

        # Add every group to the summary
        groups = source.get_groups()
        for group_id, group_name in groups.items():
            summary.add_group(group_id, group_name)

        # process every item into the summary
        items = source.get_items()
        for item in items:
            summary.add(item.group_id, item.bucket_idx, item.value)

        return summary

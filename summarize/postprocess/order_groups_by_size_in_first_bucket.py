from summarize.postprocess.i_postprocessor import IPostprocessor
from summarize.summary import Summary


class OrderGroupsBySizeInFirstBucket(IPostprocessor):

    def execute(self, summary: Summary) -> None:
        summary.groups = \
            {k: v for k, v in sorted(
                summary.groups.items(),
                key=lambda item: item[1].data[0], reverse=True)}

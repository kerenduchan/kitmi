from summarize.postprocess.i_postprocessor import IPostprocessor
from summarize.summary import Summary


class CalcTotals(IPostprocessor):

    def execute(self, summary: Summary) -> None:

        # calc total per group
        for g_id, g in summary.groups.items():
                g.total = 0
                for value in g.data:
                    g.total += value

        # calc total per bucket
        for bucket_idx, b in enumerate(summary.buckets):
            for g_id, g in summary.groups.items():
                summary.totals[bucket_idx] += g.get(bucket_idx)

        # calc total of totals
        for bucket_idx, b in enumerate(summary.buckets):
            summary.totals[len(summary.totals) - 1] += summary.totals[bucket_idx]
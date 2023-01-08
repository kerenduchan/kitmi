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
        summary.bucket_totals = [0 for i in range(summary.get_buckets_count())]
        for bucket_idx, b in enumerate(summary.buckets):
            for g_id, g in summary.groups.items():
                summary.bucket_totals[bucket_idx] += g.get(bucket_idx)

        # calc total
        summary.sum_total = 0
        for bucket_total in summary.bucket_totals:
            summary.sum_total += bucket_total

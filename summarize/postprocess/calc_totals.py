from summarize.postprocess.i_postprocessor import IPostprocessor
from summarize.summary import Summary


class CalcTotals(IPostprocessor):

    def execute(self, summary: Summary) -> None:
        for g_id, g in summary.groups.items():
                g.total = 0
                for value in g.data:
                    g.total += value

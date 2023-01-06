from summarize.postprocess.i_postprocessor import IPostprocessor
from summarize.summary import Summary


class ReverseSign(IPostprocessor):

    def execute(self, summary: Summary) -> None:
        for g_id, g in summary.groups.items():
            for i in range(len(g.data)):
                g.set(i, -g.get(i))

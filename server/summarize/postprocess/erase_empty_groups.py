from summarize.postprocess.i_postprocessor import IPostprocessor
from summarize.summary import Summary


class EraseEmptyGroups(IPostprocessor):

    def execute(self, summary: Summary) -> None:
        """ Erase groups that are all zeros """
        non_empty_groups = {}
        for g_id, g in summary.groups.items():
            if not g.is_empty():
                non_empty_groups[g_id] = g

        summary.groups = non_empty_groups

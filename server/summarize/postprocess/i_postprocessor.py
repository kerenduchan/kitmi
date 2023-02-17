import abc
from summarize.summary import Summary


class IPostprocessor(abc.ABC):
    """ Base class for all postprocessors """

    @abc.abstractmethod
    def execute(self, summary: Summary) -> None:
        pass

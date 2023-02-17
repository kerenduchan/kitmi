import abc
import typing
import summarize.summary_source_item


class ISummarySource(abc.ABC):
    """ Base class for all summary sources """

    @abc.abstractmethod
    def load(self) -> None:
        pass

    @abc.abstractmethod
    def get_groups(self) -> typing.Dict[int, str]:
        pass

    @abc.abstractmethod
    def get_buckets(self) -> typing.List[int]:
        pass

    @abc.abstractmethod
    def get_items(self) -> typing.List[summarize.summary_source_item.SummarySourceItem]:
        pass

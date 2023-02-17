from summarize.postprocess.i_postprocessor import IPostprocessor
from summarize.summary import Summary
from summarize.summary_for_one_group import SummaryForOneGroup


class MergeUnderThreshold(IPostprocessor):

    def execute(self, summary: Summary) -> None:
        buckets_count = summary.get_buckets_count()

        # create a group for "Other"
        other = SummaryForOneGroup(0, "Other", buckets_count)

        # for each bucket: _merge_under_threshold_for_bucket
        for bucket_idx in range(buckets_count):
            self._merge_under_threshold_for_bucket(summary, bucket_idx, other)

        # add the "Other" group to the summary if it is not empty
        if not other.is_empty():
            summary.groups[0] = other

    def _merge_under_threshold_for_bucket(self,
                                          summary: Summary,
                                          bucket_idx: int,
                                          other: SummaryForOneGroup) -> None:

        # list of (group_id, data) for this bucket_id for all groups
        bucket_data = summary.get_data_for_bucket(bucket_idx)

        # sort by the data (amount)
        bucket_data.sort(key=lambda d: d[1])

        # remove any negative or zero data
        first_positive_idx = self._find_first_positive_value(bucket_data)
        bucket_data = bucket_data[first_positive_idx:]

        # compute threshold for this bucket
        bucket_sum = 0
        for group_id, data in bucket_data:
            bucket_sum += data

        threshold = int(bucket_sum / 10)

        # merge groups under threshold only if there is more than one to merge
        threshold_idx = self._find_threshold_idx(bucket_data, threshold)

        if threshold_idx < 1:
            return

        for i in range(threshold_idx + 1):
            (group_id, value) = bucket_data[i]
            other.add(bucket_idx, value)
            summary.set(group_id, bucket_idx, 0)

    # return the first index in bucket_data where the value is > 0
    @staticmethod
    def _find_first_positive_value(bucket_data):
        idx = 0
        for group_id, data in bucket_data:
            if data > 0:
                return idx
            idx += 1
        return idx

    # return the first index in bucket_data where the sums up
    # until this index are below the given threshold.
    @staticmethod
    def _find_threshold_idx(bucket_data, threshold: int):
        partial_sum = 0
        idx = -1
        for group_id, data in bucket_data:
            partial_sum += data
            if partial_sum > threshold:
                return idx
            idx += 1
        return idx

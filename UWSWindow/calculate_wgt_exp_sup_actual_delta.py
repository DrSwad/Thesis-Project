from typing import Optional

from Types.types import (
    ItemProbability,
    SequenceIndex,
    SetIndex,
    USequence,
    WeightedExpectedSupport,
)
from UWSWindow.find_all_possible_occurrences_in_sequence import (
    find_all_possible_occurrences_in_sequence,
)
from UWSWindow.IncrementalTrieNode import IncrementalTrieNode


def calculate_wgt_exp_sup_actual_delta(
    root_node: IncrementalTrieNode,
    parent_node: Optional[IncrementalTrieNode],
    cur_node: IncrementalTrieNode,
    seq_index: SequenceIndex,
    sequence: USequence,
    precalculated_current_itemset_all_occurrences: Optional[
        list[tuple[SetIndex, ItemProbability]]
    ] = None,
) -> WeightedExpectedSupport:
    if precalculated_current_itemset_all_occurrences is None:
        current_itemset_all_occurrences = find_all_possible_occurrences_in_sequence(
            root_node,
            parent_node,
            cur_node,
            seq_index,
            sequence,
        )
        if len(current_itemset_all_occurrences) > 0:
            cur_node.wgt_exp_sup_actual_dp[seq_index] = current_itemset_all_occurrences
    else:
        current_itemset_all_occurrences = precalculated_current_itemset_all_occurrences

    if cur_node is root_node:
        return 0.0
    else:
        max_support: ItemProbability = 0.0
        for set_index, set_support in current_itemset_all_occurrences:
            max_support = max(max_support, set_support)

        return max_support * cur_node.ancestor_path_wgt_sum / cur_node.ancestor_path_len

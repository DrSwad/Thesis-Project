from typing import Optional

from Types.types import (
    ExtensionType,
    ItemProbability,
    SequenceIndex,
    SetIndex,
    USequence,
)
from UWSWindow.IncrementalTrieNode import IncrementalTrieNode


def find_all_possible_occurrences_in_sequence(
    root_node: IncrementalTrieNode,
    parent_node: Optional[IncrementalTrieNode],
    cur_node: IncrementalTrieNode,
    seq_index: SequenceIndex,
    sequence: USequence,
) -> list[tuple[SetIndex, ItemProbability]]:
    current_itemset_all_occurrences: list[tuple[SetIndex, ItemProbability]] = []

    if cur_node is root_node:
        current_itemset_all_occurrences.append((-1, 1.0))
        return current_itemset_all_occurrences

    assert parent_node is not None
    assert cur_node.item_id is not None

    if cur_node.extension_type == ExtensionType.i:
        for set_index, parent_itemset_prob in parent_node.wgt_exp_sup_actual_dp.get(
            seq_index, []
        ):
            itemset = sequence[set_index]
            if cur_node.item_id in itemset:
                current_itemset_all_occurrences.append(
                    (set_index, parent_itemset_prob * itemset[cur_node.item_id])
                )
    else:
        parent_dp_index = 0
        parent_dp = parent_node.wgt_exp_sup_actual_dp.get(seq_index, [])
        parent_dp_prefix_max: ItemProbability = 0.0

        for set_index in range(0, len(sequence)):
            itemset = sequence[set_index]
            if cur_node.item_id in itemset:
                while (
                    parent_dp_index < len(parent_dp)
                    and parent_dp[parent_dp_index][0] < set_index
                ):
                    parent_dp_prefix_max = max(
                        parent_dp_prefix_max,
                        parent_dp[parent_dp_index][1],
                    )
                    parent_dp_index += 1

                current_itemset_all_occurrences.append(
                    (set_index, parent_dp_prefix_max * itemset[cur_node.item_id])
                )

    return current_itemset_all_occurrences

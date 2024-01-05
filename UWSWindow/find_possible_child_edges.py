from bisect import bisect_right

from Types.types import (
    Edge,
    ExtensionType,
    ItemID,
    Itemset,
    ItemWeight,
    SequenceIndex,
    SetIndex,
    UItemset,
    USequence,
    WeightMap,
)
from UWSWindow.IncrementalTrieNode import IncrementalTrieNode


def find_possible_child_edges(
    cur_node: IncrementalTrieNode,
    sequence: USequence,
    found_at_itemset_index: SetIndex,
    item_weights: WeightMap,
) -> tuple[ItemWeight, dict[Edge, SetIndex]]:
    current_sequence_proj_max_wgt: ItemWeight = 0.0
    possible_child_edges: dict[Edge, SetIndex] = dict()

    for set_index in range(
        max(found_at_itemset_index, 0),
        len(sequence),
    ):
        itemset = sequence[set_index]

        item_ids = itemset.keys()
        start_item_id: int
        if set_index == found_at_itemset_index:
            assert cur_node.item_id is not None
            start_item_id = bisect_right(item_ids, cur_node.item_id)
        else:
            start_item_id = 0

        for index in range(start_item_id, len(item_ids)):
            item_id = item_ids[index]

            if (
                cur_node.item_id is not None
                and item_id > cur_node.item_id
                and cur_node.item_id in itemset
                and sequence_is_in_itemset(itemset, cur_node.cur_itemset)
                and (item_id, ExtensionType.i) not in possible_child_edges
            ):
                possible_child_edges[(item_id, ExtensionType.i)] = set_index

            if (
                set_index > found_at_itemset_index
                and (item_id, ExtensionType.s) not in possible_child_edges
            ):
                possible_child_edges[(item_id, ExtensionType.s)] = set_index

            # We need wgt_cap for wgt_exp_sup_cap_delta
            assert item_id in item_weights
            item_weight = item_weights[item_id]
            current_sequence_proj_max_wgt = max(
                current_sequence_proj_max_wgt, item_weight
            )

    return (current_sequence_proj_max_wgt, possible_child_edges)


def sequence_is_in_itemset(superset: UItemset, subset: Itemset) -> bool:
    for item_id in subset:
        if item_id not in superset:
            return False
    return True

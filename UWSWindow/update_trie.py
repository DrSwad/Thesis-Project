import copy
from typing import Optional

from sortedcontainers import SortedList

from Types.types import (
    Edge,
    ExtensionType,
    ItemProbability,
    Itemset,
    IUDatabase,
    SetIndex,
    WeightedExpectedSupport,
    WeightMap,
)
from UWSWindow.calculate_wgt_exp_sup_actual_delta import (
    calculate_wgt_exp_sup_actual_delta,
)
from UWSWindow.find_possible_child_edges import find_possible_child_edges
from UWSWindow.IncrementalTrieNode import IncrementalTrieNode


def update_trie(
    iu_SDB: IUDatabase,
    ip_SDB: IUDatabase,
    item_weights: WeightMap,
    minSemiWES: WeightedExpectedSupport,
    root_node: IncrementalTrieNode,
    parent_node: Optional[IncrementalTrieNode] = None,
    cur_node: Optional[IncrementalTrieNode] = None,
) -> None:
    if cur_node is None:
        cur_node = root_node

    current_database_first_sequence_index = ip_SDB[0][0]
    current_database_last_sequence_index = ip_SDB[-1][0]

    # If the first precomputed sequence in the child node has already been removed from the database,
    # remove it from the child node results too
    for child_node in cur_node.descendants.values():
        while (
            len(child_node.proj_SDB) > 0
            and child_node.proj_SDB.peekitem(0)[0]
            < current_database_first_sequence_index
        ):
            seq_index = child_node.proj_SDB.popitem(0)[0]

            child_node.ancestor_path_max_pr.pop(seq_index, None)

            child_node.wgt_exp_sup_cap -= child_node.wgt_exp_sup_cap_dp.pop(
                seq_index, 0.0
            )

            current_itemset_all_occurrences = child_node.wgt_exp_sup_actual_dp.pop(
                seq_index, []
            )
            wgt_exp_sup_actual_delta = calculate_wgt_exp_sup_actual_delta(
                root_node,
                parent_node,
                child_node,
                seq_index,
                [],
                current_itemset_all_occurrences,
            )
            child_node.wgt_exp_sup_actual -= wgt_exp_sup_actual_delta

    # If there are new sequences in the database, then process them in the current node
    for iu_seq, ip_seq in zip(reversed(iu_SDB), reversed(ip_SDB)):
        seq_index, u_sequence = iu_seq
        seq_index, p_sequence = ip_seq

        if seq_index <= cur_node.last_processed_seq_index:
            break

        found_at_itemset_index: Optional[SetIndex]
        if cur_node is root_node:
            found_at_itemset_index = -1
        elif seq_index in cur_node.proj_SDB:
            found_at_itemset_index = cur_node.proj_SDB[seq_index]
        else:
            found_at_itemset_index = None

        if found_at_itemset_index is None:
            continue

        # Calculate wgt_exp_sup_cap and corresponding dp, and find possible child edges
        current_sequence_proj_max_wgt, possible_child_edges = find_possible_child_edges(
            cur_node, p_sequence, found_at_itemset_index, item_weights
        )

        # Update data of children
        for child_edge in possible_child_edges:
            # Create child node if not created yet
            if child_edge not in cur_node.descendants:
                create_new_child_node(cur_node, child_edge, item_weights)

            child_node = cur_node.descendants[child_edge]
            child_found_at_itemset_index = possible_child_edges[child_edge]

            # Update proj_SDB of child_node
            child_node.proj_SDB[seq_index] = child_found_at_itemset_index

            # Update ancestor_path_max_pr of child_node
            assert child_node.item_id is not None
            child_node_item_sup: ItemProbability = p_sequence[
                child_found_at_itemset_index
            ][child_node.item_id]
            child_node.ancestor_path_max_pr[seq_index] = (
                1.0
                if cur_node is root_node
                else cur_node.ancestor_path_max_pr[seq_index]
            ) * child_node_item_sup

            # Update wgt_exp_sup_cap and corresponding dp of child node
            wgt_cap = max(cur_node.ancestor_path_max_wgt, current_sequence_proj_max_wgt)
            exp_cap = child_node.ancestor_path_max_pr[seq_index]
            wgt_exp_sup_cap_delta = wgt_cap * exp_cap
            child_node.wgt_exp_sup_cap += wgt_exp_sup_cap_delta
            child_node.wgt_exp_sup_cap_dp[seq_index] = wgt_exp_sup_cap_delta

        # Calculate wgt_exp_sup_actual and corresponding dp
        wgt_exp_sup_actual_delta = calculate_wgt_exp_sup_actual_delta(
            root_node, parent_node, cur_node, seq_index, u_sequence
        )
        cur_node.wgt_exp_sup_actual += wgt_exp_sup_actual_delta

    cur_node.last_processed_seq_index = current_database_last_sequence_index

    # If the node is root or is semi-frequent, then explore it's children
    eps = 0.000000001
    # Explore and possibly expand under the new node
    for child_node in cur_node.descendants.values():
        if child_node.wgt_exp_sup_cap + eps >= minSemiWES:
            update_trie(
                iu_SDB,
                ip_SDB,
                item_weights,
                minSemiWES,
                root_node,
                cur_node,
                child_node,
            )

    return


def create_new_child_node(
    parent_node: IncrementalTrieNode, child_edge: Edge, item_weights: WeightMap
) -> None:
    child_item_id, child_extension_type = child_edge

    child_itemset: Itemset = (
        copy.deepcopy(parent_node.cur_itemset)
        if child_extension_type == ExtensionType.i
        else SortedList()
    )
    child_itemset.add(child_item_id)

    assert child_item_id in item_weights
    child_item_weight = item_weights[child_item_id]

    parent_node.descendants[
        (
            child_item_id,
            child_extension_type,
        )
    ] = IncrementalTrieNode(
        extension_type=child_extension_type,
        item_id=child_item_id,
        cur_itemset=child_itemset,
        ancestor_path_max_wgt=max(parent_node.ancestor_path_max_wgt, child_item_weight),
        ancestor_path_wgt_sum=parent_node.ancestor_path_wgt_sum + child_item_weight,
        ancestor_path_len=parent_node.ancestor_path_len + 1,
    )

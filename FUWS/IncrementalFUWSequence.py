import copy
from bisect import bisect_right
from typing import Optional

from sortedcontainers import SortedList

from DataStructures.IncrementalTrie import IncrementalTrie, IncrementalTrieNode
from Parameters.ProgramVariable import ProgramVariable
from Parameters.Variable import Variable
from Types.types import (
    ExtensionType,
    ItemID,
    ItemProbability,
    Itemset,
    ItemWeight,
    SequenceIndex,
    SetIndex,
    UItemset,
    USequence,
    WeightedExpectedSupport,
)
from UtilityTechniques.ThresholdCalculation import ThresholdCalculation


class IncrementalFUWSequence:
    def __init__(self) -> None:
        self.trie = IncrementalTrie(
            IncrementalTrieNode(
                extension_type=None,
                item_id=None,
                cur_itemset=SortedList(),
                ancestor_path_max_wgt=0,
                ancestor_wgt_sum=0,
                ancestor_path_len=0,
            )
        )

        return

    def update_trie(
        self,
        parent_node: Optional[IncrementalTrieNode] = None,
        cur_node: Optional[IncrementalTrieNode] = None,
    ) -> None:
        if cur_node is None:
            cur_node = self.trie.root_node

        print(cur_node.item_id)

        # If the first sequence in the current node has already been removed from the database,
        # remove it from the current node too
        while (
            len(cur_node.proj_SDB) > 0
            and cur_node.proj_SDB.peekitem(0)[0] < ProgramVariable.ipSDB[0][0]
        ):
            seq_index = cur_node.proj_SDB.popitem(0)[0]

            cur_node.ancestor_path_max_pr.pop(seq_index)

            cur_node.wgt_exp_sup_cap -= cur_node.wgt_exp_sup_cap_dp.pop(seq_index, 0.0)

            current_itemset_all_occurrences = cur_node.wgt_exp_sup_actual_dp.pop(
                seq_index, []
            )
            wgt_exp_sup_actual_delta = self.calculate_wgt_exp_sup_actual_delta(
                parent_node, cur_node, seq_index, [], current_itemset_all_occurrences
            )
            cur_node.wgt_exp_sup_actual -= wgt_exp_sup_actual_delta

        # If there are new sequences in the database, then add them in the current node
        current_last_sequence_index = (
            -1 if len(cur_node.proj_SDB) == 0 else cur_node.proj_SDB.peekitem(-1)[0]
        )
        all_possible_child_edges: set[tuple[ExtensionType, ItemID]] = set()
        for ip_seq, iu_seq in zip(
            reversed(ProgramVariable.ipSDB), reversed(ProgramVariable.iuSDB)
        ):
            seq_index, p_sequence = ip_seq
            seq_index, u_sequence = iu_seq

            if seq_index <= current_last_sequence_index:
                break

            # Find projection of cur_node in the current sequence
            found_at_itemset_index = self.find_projection_in_sequence(
                parent_node, cur_node, seq_index, p_sequence
            )

            # Update proj_SDB and ancestor_path_max_pr of cur_node
            if found_at_itemset_index is not None:
                cur_node.proj_SDB[seq_index] = found_at_itemset_index

                current_node_item_sup: ItemProbability
                if found_at_itemset_index == -1:
                    current_node_item_sup = 1.0
                else:
                    assert cur_node.item_id is not None
                    current_node_item_sup = p_sequence[found_at_itemset_index][
                        cur_node.item_id
                    ]

                cur_node.ancestor_path_max_pr[seq_index] = (
                    1.0
                    if parent_node is None
                    else parent_node.ancestor_path_max_pr.get(seq_index, 0.0)
                ) * current_node_item_sup

            # Calculate wgt_exp_sup_cap and corresponding dp, and find possible child edges
            (
                wgt_exp_sup_cap_delta,
                possible_child_edges,
            ) = self.calculate_wgt_exp_sup_cap_delta_and_find_possible_child_edges(
                cur_node, seq_index, p_sequence, found_at_itemset_index
            )
            cur_node.wgt_exp_sup_cap += wgt_exp_sup_cap_delta
            cur_node.wgt_exp_sup_cap_dp[seq_index] = wgt_exp_sup_cap_delta

            if cur_node.wgt_exp_sup_cap < ThresholdCalculation.get_semi_wgt_exp_sup():
                return

            for child_edge in possible_child_edges:
                if child_edge not in all_possible_child_edges:
                    all_possible_child_edges.add(child_edge)

            # Calculate wgt_exp_sup_actual and corresponding dp
            wgt_exp_sup_actual_delta = self.calculate_wgt_exp_sup_actual_delta(
                parent_node, cur_node, seq_index, u_sequence
            )
            cur_node.wgt_exp_sup_actual += wgt_exp_sup_actual_delta

        # create new children nodes if not created yet
        for child_extension_type, child_item_id in all_possible_child_edges:
            if (
                child_item_id,
                child_extension_type,
            ) not in cur_node.descendants:
                child_itemset: Itemset = (
                    copy.deepcopy(cur_node.cur_itemset)
                    if child_extension_type == ExtensionType.i
                    else SortedList()
                )
                child_itemset.add(child_item_id)

                assert child_item_id in ProgramVariable.wgt_dic
                child_item_weight = ProgramVariable.wgt_dic[child_item_id]

                cur_node.descendants[
                    (
                        child_item_id,
                        child_extension_type,
                    )
                ] = IncrementalTrieNode(
                    extension_type=child_extension_type,
                    item_id=child_item_id,
                    cur_itemset=child_itemset,
                    ancestor_path_max_wgt=max(
                        cur_node.ancestor_path_max_wgt, child_item_weight
                    ),
                    ancestor_wgt_sum=cur_node.ancestor_path_wgt_sum + child_item_weight,
                    ancestor_path_len=cur_node.ancestor_path_len + 1,
                )

        # If the node is root or is semi-frequent, then explore it's children
        if (
            cur_node is self.trie.root_node
            or cur_node.wgt_exp_sup_actual + Variable.eps
            >= ThresholdCalculation.get_semi_wgt_exp_sup()
        ):
            # Explore and possibly expand under the new node
            for child_node in cur_node.descendants.values():
                self.update_trie(cur_node, child_node)

        return

    def sequence_is_in_itemset(self, superset: UItemset, subset: Itemset) -> bool:
        for item_id in subset:
            if item_id not in superset:
                return False
        return True

    def find_projection_in_sequence(
        self,
        parent_node: Optional[IncrementalTrieNode],
        cur_node: IncrementalTrieNode,
        seq_index: SequenceIndex,
        sequence: USequence,
    ) -> Optional[SetIndex]:
        found_at_itemset_index: Optional[SetIndex] = None

        if cur_node is self.trie.root_node:
            found_at_itemset_index = -1
            return found_at_itemset_index

        assert parent_node is not None
        if seq_index not in parent_node.proj_SDB:
            return found_at_itemset_index

        parent_proj_set_index = parent_node.proj_SDB[seq_index]
        start_set_index: SetIndex
        end_set_index: SetIndex

        if cur_node.extension_type == ExtensionType.i:
            start_set_index = parent_proj_set_index
            end_set_index = len(sequence)
        else:
            start_set_index = parent_proj_set_index + 1
            end_set_index = len(sequence)

        for set_index in range(start_set_index, end_set_index):
            itemset = sequence[set_index]
            if cur_node.item_id in itemset and (
                cur_node.extension_type != ExtensionType.i
                or self.sequence_is_in_itemset(itemset, cur_node.cur_itemset)
            ):
                found_at_itemset_index = set_index
                return found_at_itemset_index

        return found_at_itemset_index

    def calculate_wgt_exp_sup_cap_delta_and_find_possible_child_edges(
        self,
        cur_node: IncrementalTrieNode,
        seq_index: SequenceIndex,
        sequence: USequence,
        found_at_itemset_index: Optional[SetIndex],
    ) -> tuple[WeightedExpectedSupport, set[tuple[ExtensionType, ItemID]]]:
        current_sequence_proj_max_wgt: ItemWeight = 0.0
        wgt_exp_sup_cap_delta: WeightedExpectedSupport = 0.0
        possible_child_edges: set[tuple[ExtensionType, ItemID]] = set()

        if found_at_itemset_index is None:
            return (wgt_exp_sup_cap_delta, possible_child_edges)

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
                    and self.sequence_is_in_itemset(itemset, cur_node.cur_itemset)
                    and cur_node.item_id in itemset
                ):
                    possible_child_edges.add((ExtensionType.i, item_id))

                if set_index > found_at_itemset_index:
                    possible_child_edges.add((ExtensionType.s, item_id))

                # We need wgt_cap for wgt_exp_sup_cap_delta
                assert item_id in ProgramVariable.wgt_dic
                item_weight = ProgramVariable.wgt_dic[item_id]
                current_sequence_proj_max_wgt = max(
                    current_sequence_proj_max_wgt, item_weight
                )

        # Calculate wgt_exp_sup_cap_delta
        wgt_cap = max(cur_node.ancestor_path_max_wgt, current_sequence_proj_max_wgt)
        exp_cap = cur_node.ancestor_path_max_pr[seq_index]
        wgt_exp_sup_cap_delta = exp_cap * wgt_cap

        return (wgt_exp_sup_cap_delta, possible_child_edges)

    def calculate_wgt_exp_sup_actual_delta(
        self,
        parent_node: Optional[IncrementalTrieNode],
        cur_node: IncrementalTrieNode,
        seq_index: SequenceIndex,
        sequence: USequence,
        precalculated_current_itemset_all_occurrences: Optional[
            list[tuple[SetIndex, ItemProbability]]
        ] = None,
    ) -> WeightedExpectedSupport:
        if precalculated_current_itemset_all_occurrences is None:
            current_itemset_all_occurrences = (
                self.find_all_possible_occurrences_in_sequence(
                    parent_node,
                    cur_node,
                    seq_index,
                    sequence,
                )
            )
            if len(current_itemset_all_occurrences) > 0:
                cur_node.wgt_exp_sup_actual_dp[
                    seq_index
                ] = current_itemset_all_occurrences
        else:
            current_itemset_all_occurrences = (
                precalculated_current_itemset_all_occurrences
            )

        if cur_node is self.trie.root_node:
            return 0.0
        else:
            max_support: ItemProbability = 0.0
            for set_index, set_support in current_itemset_all_occurrences:
                max_support = max(max_support, set_support)

            return (
                max_support
                * cur_node.ancestor_path_wgt_sum
                / cur_node.ancestor_path_len
            )

    def find_all_possible_occurrences_in_sequence(
        self,
        parent_node: Optional[IncrementalTrieNode],
        cur_node: IncrementalTrieNode,
        seq_index: SequenceIndex,
        sequence: USequence,
    ) -> list[tuple[SetIndex, ItemProbability]]:
        current_itemset_all_occurrences: list[tuple[SetIndex, ItemProbability]] = []

        if cur_node is self.trie.root_node:
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

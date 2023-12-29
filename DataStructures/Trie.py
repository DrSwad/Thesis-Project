import copy
from typing import IO, Optional

from Parameters.FileInfo import FileInfo
from Parameters.ProgramVariable import ProgramVariable
from Parameters.Variable import Variable
from Types.types import (
    ExtensionType,
    ItemID,
    ItemProbability,
    ItemWeight,
    WeightedExpectedSupport,
)
from UtilityTechniques.ThresholdCalculation import ThresholdCalculation


class TrieNode:
    def __init__(
        self,
        semi_frequent: bool,
        extension_type: Optional[ExtensionType],
        item_id: Optional[ItemID],
        support_value: WeightedExpectedSupport,
    ) -> None:
        self.semi_frequent = semi_frequent
        self.extension_type = extension_type
        self.item_id = item_id  # Rename to item_id
        self.support_value = support_value
        self.descendants: dict[tuple[ItemID, ExtensionType], TrieNode] = dict()


class Trie:
    def __init__(self, root_node: TrieNode):
        self.root_node = root_node
        return

    def prepare_trie_for_actual_support_calculation(
        self, cur_node: Optional[TrieNode] = None
    ) -> None:
        if cur_node is None:
            cur_node = self.root_node

        if cur_node.semi_frequent:
            cur_node.support_value = 0.0

        for child_node in cur_node.descendants.values():
            self.prepare_trie_for_actual_support_calculation(child_node)

    def actual_support_calculation(
        self,
        seq_index: int,
        cur_node: Optional[TrieNode] = None,
        seq_wgt_sum: ItemWeight = 0,
        current_itemset_all_occurrences: Optional[
            list[tuple[int, ItemProbability]]
        ] = None,
        cur_ln: int = 0,
    ) -> None:
        if cur_node is None:
            cur_node = self.root_node

        if current_itemset_all_occurrences is None:
            current_itemset_all_occurrences = [(-1, 1.0)]

        for child_node in cur_node.descendants.values():
            assert child_node.item_id is not None
            assert child_node.extension_type is not None

            new_itemset_all_occurrences = self.find_all_possible_extensions_in_sequence(
                child_node.extension_type,
                child_node.item_id,
                seq_index,
                []
                if current_itemset_all_occurrences is None
                else current_itemset_all_occurrences,
            )

            new_ln = cur_ln + 1
            assert child_node.item_id in ProgramVariable.wgt_dic
            new_seq_wgt_sum = seq_wgt_sum + float(
                ProgramVariable.wgt_dic[child_node.item_id]
            )
            child_node_max_exp = 0.0
            for set_index, itemset_prob in new_itemset_all_occurrences:
                child_node_max_exp = max(child_node_max_exp, itemset_prob)
            child_node.support_value += (child_node_max_exp * new_seq_wgt_sum) / new_ln

            self.actual_support_calculation(
                seq_index,
                child_node,
                new_seq_wgt_sum,
                new_itemset_all_occurrences,
                new_ln,
            )

        return

    def find_all_possible_extensions_in_sequence(
        self,
        extension_type: ExtensionType,
        item_id: ItemID,
        seq_index: int,
        current_itemset_all_occurrences: list[tuple[int, ItemProbability]],
    ) -> list[tuple[int, ItemProbability]]:
        new_set_indices: list[tuple[int, ItemProbability]] = []

        if extension_type == ExtensionType.i:
            for set_index, cur_itemset_prob in current_itemset_all_occurrences:
                itemset = ProgramVariable.uSDB[seq_index][set_index]
                if item_id in itemset:
                    new_set_indices.append(
                        (set_index, cur_itemset_prob * itemset[item_id])
                    )
        else:
            set_indices_index = 0
            current_itemset_prob_prefix_max: ItemProbability = 0.0

            for set_index in range(0, len(ProgramVariable.uSDB[seq_index])):
                itemset = ProgramVariable.uSDB[seq_index][set_index]
                if item_id in itemset:
                    while (
                        set_indices_index < len(current_itemset_all_occurrences)
                        and current_itemset_all_occurrences[set_indices_index][0]
                        < set_index
                    ):
                        current_itemset_prob_prefix_max = max(
                            current_itemset_prob_prefix_max,
                            current_itemset_all_occurrences[set_indices_index][1],
                        )
                        set_indices_index += 1

                    new_set_indices.append(
                        (set_index, current_itemset_prob_prefix_max * itemset[item_id])
                    )

        return new_set_indices

    def evaluate_semi_frequency_flags(
        self, cur_node: Optional[TrieNode] = None
    ) -> None:
        if cur_node is None:
            cur_node = self.root_node

        if (
            cur_node is self.root_node
            or cur_node.support_value + Variable.eps
            >= ThresholdCalculation.get_semi_wgt_exp_sup()
        ):
            cur_node.semi_frequent = True
        else:
            cur_node.semi_frequent = False

        for child_node in cur_node.descendants.values():
            self.evaluate_semi_frequency_flags(child_node)

        return

    def only_keep_semi_frequent_nodes(self, cur_node: Optional[TrieNode] = None) -> int:
        if cur_node is None:
            cur_node = self.root_node

        descendants_copy = copy.deepcopy(cur_node.descendants)
        cur_node.descendants = dict()

        for child_edge, child_node in descendants_copy.items():
            children_size = self.only_keep_semi_frequent_nodes(child_node)
            if children_size > 0:
                cur_node.descendants[child_edge] = child_node

        return len(cur_node.descendants) + cur_node.semi_frequent

    def log_semi_frequent_nodes_in_trie(
        self,
        file: Optional[IO[str]] = None,
        lower_limit: Optional[WeightedExpectedSupport] = None,
        upper_limit: Optional[WeightedExpectedSupport] = None,
        cur_node: Optional[TrieNode] = None,
        cur_seq: Optional[str] = None,
    ) -> None:
        if cur_node is None:
            cur_node = self.root_node
        if cur_seq is None:
            cur_seq = ""

        if cur_node.extension_type == ExtensionType.i and cur_node.item_id is not None:
            cur_seq = cur_seq[: len(cur_seq) - 1] + cur_node.item_id + ")"
        elif cur_node.item_id is not None:
            cur_seq = cur_seq + "(" + cur_node.item_id + ")"

        if (
            cur_node.semi_frequent
            and cur_node is not self.root_node
            and (lower_limit is None or cur_node.support_value >= lower_limit)
            and (upper_limit is None or cur_node.support_value < upper_limit)
        ):
            if file is None:
                print(cur_seq)
            else:
                assert file is not None
                file.write(cur_seq)
                file.write(": ")
                file.write(str(round(cur_node.support_value, 2)))
                file.write("\n")

        for child_node in cur_node.descendants.values():
            self.log_semi_frequent_nodes_in_trie(
                file, lower_limit, upper_limit, child_node, cur_seq
            )

        return

    def merge_ls_with_fssfs_trie(
        self, cur_node_ls: TrieNode, cur_node_fssfs: TrieNode
    ) -> None:
        for child_edge in cur_node_ls.descendants:
            if child_edge in cur_node_fssfs.descendants:
                self.merge_ls_with_fssfs_trie(
                    cur_node_ls.descendants[child_edge],
                    cur_node_fssfs.descendants[child_edge],
                )
            elif (
                cur_node_ls.descendants[child_edge].support_value + Variable.eps
                >= ThresholdCalculation.get_semi_wgt_exp_sup()
            ):
                self.insert_node(
                    cur_node_fssfs,
                    child_edge,
                    cur_node_ls.descendants[child_edge].support_value,
                )
                self.merge_ls_with_fssfs_trie(
                    cur_node_ls.descendants[child_edge],
                    cur_node_fssfs.descendants[child_edge],
                )
        return

    def insert_node(
        self,
        cur_node: TrieNode,
        new_edge: tuple[ItemID, ExtensionType],
        support_value: WeightedExpectedSupport,
    ) -> None:
        item_id, extension_type = new_edge
        new_node = TrieNode(True, extension_type, item_id, support_value)
        cur_node.descendants[new_edge] = new_node
        return

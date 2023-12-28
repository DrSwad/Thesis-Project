import copy
from bisect import bisect_right
from typing import Optional

from sortedcontainers import SortedDict, SortedList

from DataStructures.Trie import Trie, TrieNode
from Parameters.ProgramVariable import ProgramVariable
from Parameters.Variable import Variable
from Types.types import (
    ExpectedSupport,
    ExtensionType,
    ItemID,
    ItemProbability,
    Itemset,
    ItemWeight,
    ProjectedDatabase,
    ProjectionPosition,
)
from UtilityTechniques.ThresholdCalculation import ThresholdCalculation


class FUWSequence:
    def __init__(self) -> None:
        self.trie = Trie(TrieNode(False, None, None, 0.0))
        return

    def generate_trie_of_actual_sequences(self) -> Trie:
        # Find all the candidate sequences satisfying the threshold and construct the trie under the root
        self.generate_trie_of_candidate_sequences(
            None, self.trie.root_node, SortedList(), 1, 0, 0
        )

        # Log the candidate nodes of the trie
        self.trie.log_semi_frequent_nodes_in_trie()

        # Reset the support values of nodes to 0 and find total candidates in the trie
        self.trie.prepare_trie_for_actual_support_calculation()

        # Loop over each sequence and accumulate the actual support values at each node
        for seq_index in range(0, len(ProgramVariable.uSDB)):
            self.trie.actual_support_calculation(seq_index)

        # Update the flags indicating semi frequency at each node
        self.trie.evaluate_semi_frequency_flags()

        return self.trie

    def generate_trie_of_candidate_sequences(
        self,
        pSDB: Optional[ProjectedDatabase],
        cur_node: TrieNode,
        cur_itemset: Itemset,
        max_pr: ItemProbability,
        max_wgt: ItemWeight,
        curLen: int,
    ) -> None:
        for extension_type in [ExtensionType.i, ExtensionType.s]:
            # The first item extension must be of type s-extension
            if pSDB is None and extension_type == ExtensionType.i:
                continue

            # Find all the extension items and extension types possible from the current node
            possible_item_extensions = self.determine_extendable_items_with_projections(
                pSDB, cur_itemset, extension_type
            )

            # Calculate maximum weight in the projection database
            # to be used for wgt_cap calculation later
            proj_max_wgt = 0.0
            for item_id in possible_item_extensions:
                assert item_id in ProgramVariable.wgt_dic
                item_weight = ProgramVariable.wgt_dic[item_id]
                proj_max_wgt = max(proj_max_wgt, item_weight)

            # Try to extend with each possible item
            for item_id in possible_item_extensions:
                item_exp_sup, item_max_prob, proj_SDB = possible_item_extensions[
                    item_id
                ]

                # Calculate w_exp_sup_cap of the extended node to see if it satisfies the threshold
                assert item_id in ProgramVariable.wgt_dic
                item_weight = ProgramVariable.wgt_dic[item_id]
                wgt_cap = max(max_wgt, proj_max_wgt)
                w_exp_sup_cap = max_pr * item_exp_sup * wgt_cap

                # If the extended node is semi-frequent, then explore it
                if (
                    w_exp_sup_cap + Variable.eps
                    >= ThresholdCalculation.get_semi_wgt_exp_sup()
                ):
                    # Calculate the new working itemset by appending the current item
                    new_cur_itemset: Itemset = (
                        copy.deepcopy(cur_itemset)
                        if extension_type == ExtensionType.i
                        else SortedList()
                    )
                    new_cur_itemset.add(item_id)

                    new_len = curLen + 1 if extension_type == ExtensionType.i else 1

                    # Create a new node and add it under the parent node in the trie
                    new_node = TrieNode(True, extension_type, item_id, 0.0)
                    if (item_id, extension_type) not in cur_node.descendants:
                        cur_node.descendants[(item_id, extension_type)] = new_node

                    # Explore and possibly expand under the new node
                    self.generate_trie_of_candidate_sequences(
                        proj_SDB,
                        new_node,
                        copy.deepcopy(new_cur_itemset),
                        max_pr * item_max_prob,
                        max(item_weight, max_wgt),
                        new_len,
                    )
        return

    def determine_extendable_items_with_projections(
        self,
        projSDB: Optional[ProjectedDatabase],
        cur_item_set: Itemset,
        extension_type: ExtensionType,
    ) -> SortedDict[
        ItemID,
        tuple[ExpectedSupport, ItemProbability, ProjectedDatabase],
    ]:
        possible_item_extensions: SortedDict[
            ItemID,
            tuple[ExpectedSupport, ItemProbability, ProjectedDatabase],
        ] = SortedDict()

        for i in range(
            0, len(ProgramVariable.pSDB) if projSDB is None else len(projSDB)
        ):
            current_sequence_item_extensions: dict[
                ItemID, tuple[ItemProbability, ProjectionPosition]
            ] = dict()

            if extension_type == ExtensionType.s:
                seq_index = i if projSDB is None else projSDB[i].seq_index
                prv_set_index = -1 if projSDB is None else projSDB[i].set_index
                for set_index in range(
                    prv_set_index + 1,
                    len(ProgramVariable.pSDB[seq_index]),
                ):
                    itemset = ProgramVariable.pSDB[seq_index][set_index]
                    for item_id in itemset:
                        if item_id not in current_sequence_item_extensions:
                            current_sequence_item_extensions[item_id] = (
                                itemset[item_id],
                                ProjectionPosition(seq_index, set_index, item_id),
                            )
            else:
                assert projSDB is not None
                proj_pos = projSDB[i]
                itemset = ProgramVariable.pSDB[proj_pos.seq_index][proj_pos.set_index]
                keys = itemset.keys()
                for k in range(bisect_right(keys, proj_pos.item_id), len(keys)):
                    item_id = keys[k]
                    if item_id not in current_sequence_item_extensions:
                        current_sequence_item_extensions[item_id] = (
                            itemset[item_id],
                            ProjectionPosition(
                                proj_pos.seq_index, proj_pos.set_index, item_id
                            ),
                        )

                for set_index in range(
                    proj_pos.set_index + 1,
                    len(ProgramVariable.pSDB[proj_pos.seq_index]),
                ):
                    itemset = ProgramVariable.pSDB[proj_pos.seq_index][set_index]
                    proper_subset = True
                    if len(cur_item_set) >= len(itemset):
                        proper_subset = False
                    else:
                        for item_id in cur_item_set:
                            if item_id not in itemset:
                                proper_subset = False
                                break

                    if proper_subset:
                        keys = itemset.keys()
                        for k in range(bisect_right(keys, proj_pos.item_id), len(keys)):
                            item_id = keys[k]
                            if item_id not in current_sequence_item_extensions:
                                current_sequence_item_extensions[item_id] = (
                                    itemset[item_id],
                                    ProjectionPosition(
                                        proj_pos.seq_index, set_index, item_id
                                    ),
                                )

            for item_id in current_sequence_item_extensions:
                item_prob = current_sequence_item_extensions[item_id][0]
                item_pos = current_sequence_item_extensions[item_id][1]

                if item_id not in possible_item_extensions:
                    possible_item_extensions[item_id] = (
                        0,
                        0,
                        [],
                    )

                exp_sup = possible_item_extensions[item_id][0] + float(item_prob)
                max_prob = max(possible_item_extensions[item_id][1], item_prob)
                proj_db = possible_item_extensions[item_id][2]
                proj_db.append(item_pos)

                possible_item_extensions[item_id] = (exp_sup, max_prob, proj_db)

        return possible_item_extensions

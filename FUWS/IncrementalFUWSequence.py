import copy
from bisect import bisect_right
from typing import Optional

from sortedcontainers import SortedDict, SortedList

from DataStructures.Trie import Trie, TrieNode
from FUWS.FUWSequence import FUWSequence
from Parameters.ProgramVariable import ProgramVariable
from Parameters.Variable import Variable
from Types.types import (
    ExtensionType,
    ItemID,
    ItemProbability,
    Itemset,
    ItemWeight,
    ProjectedDatabase,
    ProjectionPosition,
    WeightedExpectedSupport,
)
from UtilityTechniques.ThresholdCalculation import ThresholdCalculation


class IncrementalFUWSequence(FUWSequence):
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

            possible_item_extensions = (
                self.incrementally_determine_extendable_items_with_projections(
                    pSDB, cur_itemset, max_pr, max_wgt, extension_type
                )
            )

            # Try to extend with each possible item
            for item_id in possible_item_extensions:
                w_exp_sup_cap, item_max_prob, proj_SDB = possible_item_extensions[
                    item_id
                ]

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
                    assert item_id in ProgramVariable.wgt_dic
                    item_weight = ProgramVariable.wgt_dic[item_id]
                    self.generate_trie_of_candidate_sequences(
                        proj_SDB,
                        new_node,
                        copy.deepcopy(new_cur_itemset),
                        max_pr * item_max_prob,
                        max(item_weight, max_wgt),
                        new_len,
                    )
        return

    def incrementally_determine_extendable_items_with_projections(
        self,
        projSDB: Optional[ProjectedDatabase],
        cur_item_set: Itemset,
        max_pr: ItemProbability,
        max_wgt: ItemWeight,
        extension_type: ExtensionType,
    ) -> SortedDict[
        ItemID,
        tuple[WeightedExpectedSupport, ItemProbability, ProjectedDatabase],
    ]:
        possible_item_extensions: SortedDict[
            ItemID,
            tuple[WeightedExpectedSupport, ItemProbability, ProjectedDatabase],
        ] = SortedDict()

        for i in range(
            0, len(ProgramVariable.pSDB) if projSDB is None else len(projSDB)
        ):
            current_sequence_item_extensions: dict[
                ItemID, tuple[ItemProbability, ItemWeight, ProjectionPosition]
            ] = dict()
            max_suffix_wgt: ItemWeight = 0.0

            if extension_type == ExtensionType.s:
                seq_index = i if projSDB is None else projSDB[i].seq_index
                prv_set_index = -1 if projSDB is None else projSDB[i].set_index

                for set_index in range(
                    len(ProgramVariable.pSDB[seq_index]) - 1, prv_set_index, -1
                ):
                    itemset = ProgramVariable.pSDB[seq_index][set_index]
                    for item_id in reversed(itemset):
                        assert item_id in ProgramVariable.wgt_dic
                        item_weight = ProgramVariable.wgt_dic[item_id]
                        max_suffix_wgt = max(max_suffix_wgt, item_weight)

                        current_sequence_item_extensions[item_id] = (
                            itemset[item_id],
                            max_suffix_wgt,
                            ProjectionPosition(seq_index, set_index, item_id),
                        )
            else:
                assert projSDB is not None
                proj_pos = projSDB[i]
                itemset = ProgramVariable.pSDB[proj_pos.seq_index][proj_pos.set_index]
                keys = itemset.keys()
                for k in range(
                    len(keys) - 1, bisect_right(keys, proj_pos.item_id) - 1, -1
                ):
                    item_id = keys[k]

                    assert item_id in ProgramVariable.wgt_dic
                    item_weight = ProgramVariable.wgt_dic[item_id]
                    max_suffix_wgt = max(max_suffix_wgt, item_weight)

                    current_sequence_item_extensions[item_id] = (
                        itemset[item_id],
                        max_suffix_wgt,
                        ProjectionPosition(
                            proj_pos.seq_index, proj_pos.set_index, item_id
                        ),
                    )

                for set_index in range(
                    len(ProgramVariable.pSDB[proj_pos.seq_index]) - 1,
                    proj_pos.set_index,
                    -1,
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
                        for k in range(
                            len(keys) - 1, bisect_right(keys, proj_pos.item_id) + 1, -1
                        ):
                            item_id = keys[k]

                            assert item_id in ProgramVariable.wgt_dic
                            item_weight = ProgramVariable.wgt_dic[item_id]
                            max_suffix_wgt = max(max_suffix_wgt, item_weight)

                            current_sequence_item_extensions[item_id] = (
                                itemset[item_id],
                                max_suffix_wgt,
                                ProjectionPosition(
                                    proj_pos.seq_index, set_index, item_id
                                ),
                            )

            for item_id in current_sequence_item_extensions:
                item_prob = current_sequence_item_extensions[item_id][0]
                max_suffix_wgt = current_sequence_item_extensions[item_id][1]
                item_pos = current_sequence_item_extensions[item_id][2]

                if item_id not in possible_item_extensions:
                    possible_item_extensions[item_id] = (
                        0,
                        0,
                        [],
                    )

                wgt_cap = max(max_wgt, max_suffix_wgt)
                wgt_exp_sup = (
                    possible_item_extensions[item_id][0] + max_pr * item_prob * wgt_cap
                )
                max_prob = max(possible_item_extensions[item_id][1], item_prob)
                proj_db = possible_item_extensions[item_id][2]
                proj_db.append(item_pos)

                possible_item_extensions[item_id] = (wgt_exp_sup, max_prob, proj_db)

        return possible_item_extensions

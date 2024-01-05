from typing import Optional

from sortedcontainers import SortedDict

from Types.types import (
    ActualDP,
    CapDP,
    Edge,
    ExtensionType,
    IProjectedDatabase,
    ItemID,
    Itemset,
    ItemWeight,
    MaxProbDP,
    WeightedExpectedSupport,
)


class IncrementalTrieNode:
    def __init__(
        self,
        extension_type: Optional[ExtensionType],
        item_id: Optional[ItemID],
        cur_itemset: Itemset,
        ancestor_path_max_wgt: ItemWeight,
        ancestor_path_wgt_sum: ItemWeight,
        ancestor_path_len: int,
    ) -> None:
        self.extension_type = extension_type
        self.item_id = item_id
        self.cur_itemset = cur_itemset
        self.ancestor_path_max_wgt = ancestor_path_max_wgt
        self.ancestor_path_wgt_sum = ancestor_path_wgt_sum
        self.ancestor_path_len = ancestor_path_len

        self.last_processed_seq_index = -1
        self.descendants: dict[Edge, IncrementalTrieNode] = dict()
        self.ancestor_path_max_pr: MaxProbDP = SortedDict()
        self.wgt_exp_sup_cap: WeightedExpectedSupport = 0.0
        self.wgt_exp_sup_actual: WeightedExpectedSupport = 0.0
        self.wgt_exp_sup_cap_dp: CapDP = SortedDict()
        self.wgt_exp_sup_actual_dp: ActualDP = SortedDict()
        self.proj_SDB: IProjectedDatabase = SortedDict()

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"({str(self.extension_type)}, {str(self.item_id)}) {self.ancestor_path_len}:{self.cur_itemset} {self.wgt_exp_sup_cap}:{self.wgt_exp_sup_actual} {self.wgt_exp_sup_cap_dp}:{self.wgt_exp_sup_actual_dp}"

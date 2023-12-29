from typing import Optional

from DataStructures.Trie import TrieNode
from Types.types import (
    ExtensionType,
    ItemID,
    ItemProbability,
    Itemset,
    ItemWeight,
    ProjectedDatabase,
    WeightedExpectedSupport,
)


class IncrementalTrieNode(TrieNode):
    def __init__(
        self,
        semi_frequent: bool,
        extension_type: Optional[ExtensionType],
        item_id: Optional[ItemID],
        support_value: WeightedExpectedSupport,
        proj_SDB: Optional[ProjectedDatabase],
        cur_itemset: Itemset,
        ancestor_max_pr: ItemProbability,
        ancestor_max_wgt: ItemWeight,
        ancestor_len: int,
    ) -> None:
        super().__init__(
            semi_frequent,
            extension_type,
            item_id,
            support_value,
        )

        self.proj_SDB = proj_SDB
        self.cur_itemset = cur_itemset
        self.ancestor_max_pr = ancestor_max_pr
        self.ancestor_max_wgt = ancestor_max_wgt
        self.ancestor_len = ancestor_len

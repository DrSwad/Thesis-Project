from typing import IO, Optional

from sortedcontainers import SortedDict

from Types.types import (
    ActualDP,
    CapDP,
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
        ancestor_wgt_sum: ItemWeight,
        ancestor_path_len: int,
    ) -> None:
        self.extension_type = extension_type
        self.item_id = item_id
        self.cur_itemset = cur_itemset
        self.ancestor_path_max_wgt = ancestor_path_max_wgt
        self.ancestor_path_wgt_sum = ancestor_wgt_sum
        self.ancestor_path_len = ancestor_path_len

        self.descendants: dict[
            tuple[ItemID, ExtensionType], IncrementalTrieNode
        ] = dict()
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


class IncrementalTrie:
    def __init__(self, root_node: IncrementalTrieNode):
        self.root_node = root_node
        return

    def log_trie(
        self,
        file: Optional[IO[str]] = None,
        lower_limit: Optional[WeightedExpectedSupport] = None,
        upper_limit: Optional[WeightedExpectedSupport] = None,
        cur_node: Optional[IncrementalTrieNode] = None,
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
            cur_node is not self.root_node
            and (lower_limit is None or cur_node.wgt_exp_sup_actual >= lower_limit)
            and (upper_limit is None or cur_node.wgt_exp_sup_actual < upper_limit)
        ):
            if file is None:
                print(f"{cur_seq}: {str(round(cur_node.wgt_exp_sup_actual, 2))}")
            else:
                assert file is not None
                file.write(f"{cur_seq}: {str(round(cur_node.wgt_exp_sup_actual, 2))}\n")

        for child_node in cur_node.descendants.values():
            self.log_trie(
                file,
                lower_limit,
                upper_limit,
                child_node,
                cur_seq,
            )

        if cur_node is self.root_node:
            if file is None:
                print("-----------")
            else:
                assert file is not None
                file.write("-----------\n")

        return

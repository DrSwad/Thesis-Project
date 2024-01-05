from typing import IO, Optional

from Types.types import ExtensionType, WeightedExpectedSupport
from UWSWindow.IncrementalTrieNode import IncrementalTrieNode


def log_trie(
    root_node: IncrementalTrieNode,
    file: Optional[IO[str]] = None,
    lower_limit: Optional[WeightedExpectedSupport] = None,
    upper_limit: Optional[WeightedExpectedSupport] = None,
    cur_node: Optional[IncrementalTrieNode] = None,
    cur_seq: Optional[str] = None,
) -> None:
    if cur_node is None:
        cur_node = root_node
    if cur_seq is None:
        cur_seq = ""

    if cur_node.extension_type == ExtensionType.i and cur_node.item_id is not None:
        cur_seq = cur_seq[: len(cur_seq) - 1] + cur_node.item_id + ")"
    elif cur_node.item_id is not None:
        cur_seq = cur_seq + "(" + cur_node.item_id + ")"

    if (
        cur_node is not root_node
        and (lower_limit is None or cur_node.wgt_exp_sup_actual >= lower_limit)
        and (upper_limit is None or cur_node.wgt_exp_sup_actual < upper_limit)
    ):
        if file is None:
            print(f"{cur_seq}: {str(round(cur_node.wgt_exp_sup_actual, 2))}")
        else:
            assert file is not None
            file.write(f"{cur_seq}: {str(round(cur_node.wgt_exp_sup_actual, 2))}\n")

    for child_node in cur_node.descendants.values():
        log_trie(
            root_node,
            file,
            lower_limit,
            upper_limit,
            child_node,
            cur_seq,
        )

    if cur_node is root_node:
        if file is None:
            print("-----------")
        else:
            file.write("-----------\n")

    return

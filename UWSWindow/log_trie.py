from typing import IO, Optional

from Types.types import ExtensionType, WeightedExpectedSupport
from UWSWindow.IncrementalTrieNode import IncrementalTrieNode


def log_trie(
    root_node: IncrementalTrieNode,
    file: Optional[IO[str]] = None,
    cap_lower_limit: Optional[WeightedExpectedSupport] = None,
    cap_upper_limit: Optional[WeightedExpectedSupport] = None,
    actual_lower_limit: Optional[WeightedExpectedSupport] = None,
    actual_upper_limit: Optional[WeightedExpectedSupport] = None,
    cur_node: Optional[IncrementalTrieNode] = None,
    cur_seq: Optional[str] = None,
    count_nodes_only: bool = False,
) -> int:
    if cur_node is None:
        cur_node = root_node
    if cur_seq is None:
        cur_seq = ""

    visited_counter = 0

    if not count_nodes_only:
        if cur_node.extension_type == ExtensionType.i and cur_node.item_id is not None:
            cur_seq = cur_seq[: len(cur_seq) - 1] + cur_node.item_id + ")"
        elif cur_node.item_id is not None:
            cur_seq = cur_seq + "(" + cur_node.item_id + ")"

    if (
        cur_node is not root_node
        and (cap_lower_limit is None or cur_node.wgt_exp_sup_cap >= cap_lower_limit)
        and (cap_upper_limit is None or cur_node.wgt_exp_sup_cap < cap_upper_limit)
        and (
            actual_lower_limit is None
            or cur_node.wgt_exp_sup_actual >= actual_lower_limit
        )
        and (
            actual_upper_limit is None
            or cur_node.wgt_exp_sup_actual < actual_upper_limit
        )
    ):
        visited_counter += 1
        if not count_nodes_only:
            if file is None:
                print(f"{cur_seq}: {str(round(cur_node.wgt_exp_sup_actual, 2))}")
            else:
                assert file is not None
                file.write(f"{cur_seq}: {str(round(cur_node.wgt_exp_sup_actual, 2))}\n")

    for child_node in cur_node.descendants.values():
        visited_counter += log_trie(
            root_node,
            file,
            cap_lower_limit,
            cap_upper_limit,
            actual_lower_limit,
            actual_upper_limit,
            child_node,
            cur_seq,
            count_nodes_only,
        )

    if not count_nodes_only and cur_node is root_node:
        if file is None:
            print("-----------")
        else:
            file.write("-----------\n")

    return visited_counter

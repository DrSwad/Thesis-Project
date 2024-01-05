import time
from collections import deque
from typing import IO

from sortedcontainers import SortedList

from Types.types import (
    ExpectedSupport,
    ItemWeight,
    IUDatabase,
    WeightedExpectedSupport,
    WeightMap,
)
from UWSWindow.IncrementalTrieNode import IncrementalTrieNode
from UWSWindow.log_trie import log_trie
from UWSWindow.read_and_process_input_database import read_and_process_input_database
from UWSWindow.update_trie import update_trie


def uWSWindow(
    input_increment_files: list[str],
    input_weight_file: str,
    output_directory: str,
    min_sup: ExpectedSupport,
    wgt_factor: ItemWeight,
    mu: float,
    window_size: int,
) -> None:
    # Initialize output file information to store results of the algorithm.
    fs = open(f"{output_directory}/fs.txt", "w")
    sfs = open(f"{output_directory}/sfs.txt", "w")
    time_info = open(f"{output_directory}/time_info_plus_v0.txt", "w")

    # WAM calculation
    wgt_file = open(input_weight_file, "r")
    item_weights: WeightMap = dict()
    total_item_freq: int = 0
    total_item_weighted_freq: float = 0.0

    # Initialize empty databases
    iu_SDB: IUDatabase = deque()
    ip_SDB: IUDatabase = deque()

    # Create the root node
    root_node = IncrementalTrieNode(
        extension_type=None,
        item_id=None,
        cur_itemset=SortedList(),
        ancestor_path_max_wgt=0,
        ancestor_path_wgt_sum=0,
        ancestor_path_len=0,
    )

    for input_increment_file in input_increment_files:
        # Load incremental data.
        dataset = open(input_increment_file, "r")

        # Preprocess dataset
        total_item_freq, total_item_weighted_freq = read_and_process_input_database(
            dataset,
            window_size,
            iu_SDB,
            ip_SDB,
            total_item_freq,
            total_item_weighted_freq,
            item_weights,
            wgt_file,
        )

        WAM = total_item_weighted_freq / total_item_freq
        size_of_dataset = len(iu_SDB)
        minWES = min_sup * size_of_dataset * wgt_factor * WAM
        minSemiWES = minWES * mu

        process_new_data(
            iu_SDB,
            ip_SDB,
            item_weights,
            root_node,
            minWES,
            minSemiWES,
            fs,
            sfs,
            time_info,
        )

        dataset.close()

    fs.close()
    sfs.close()
    time_info.close()


def process_new_data(
    iu_SDB: IUDatabase,
    ip_SDB: IUDatabase,
    item_weights: WeightMap,
    root_node: IncrementalTrieNode,
    minWES: WeightedExpectedSupport,
    minSemiWES: WeightedExpectedSupport,
    fs: IO[str],
    sfs: IO[str],
    time_info: IO[str],
) -> None:
    # Run Incremental FUWS algorithm to get FS and SFS from initial datasets and store them into USeq-Trie
    previous_time = time.time()
    update_trie(iu_SDB, ip_SDB, item_weights, minSemiWES, root_node)
    cur_time = time.time()

    # Log all the nodes of the trie
    # self.incrementalFUWSequence.trie.log_trie()

    # Log answers into file
    log_trie(root_node, fs, minWES)
    log_trie(
        root_node,
        sfs,
        minSemiWES,
        minWES,
    )

    # Log time
    time_info.write(str(cur_time - previous_time))
    time_info.write("\n")

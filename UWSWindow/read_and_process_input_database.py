from typing import IO

from sortedcontainers import SortedDict

from Types.types import (
    ItemID,
    ItemProbability,
    IUDatabase,
    UItemset,
    USequence,
    WeightMap,
)


# Returns (total_item_freq, total_item_weighted_freq)
def read_and_process_input_database(
    dataset: IO[str],
    window_size: int,
    iu_SDB: IUDatabase,
    ip_SDB: IUDatabase,
    total_item_freq: int,
    total_item_weighted_freq: float,
    item_weights: WeightMap,
    wgt_file: IO[str],
) -> tuple[int, float]:
    new_item_freq: dict[ItemID, int] = dict()

    for seq in dataset:
        p_seq: USequence = []
        u_seq: USequence = []
        rev_seq = seq[::-1]

        p_itemset: UItemset = SortedDict()
        u_itemset: UItemset = SortedDict()

        token: ItemID = ""
        val: ItemProbability = 0.0
        item_max_prob: dict[ItemID, ItemProbability] = dict()

        for ch in rev_seq:
            if ch == " ":
                ch = ""
            # Starting new itemset
            elif ch == ")":
                p_itemset = SortedDict()
                u_itemset = SortedDict()
            # Finished reading probability
            elif ch == ":":
                token = token.strip()
                token = token[::-1]
                token = token.strip()
                if len(token) == 0:
                    token = "0"
                val = float(token)
                token = ""
            # Finished reading item, and possibly itemset too
            elif ch == "," or ch == "(":
                token = token[::-1]

                u_itemset[token] = val

                if token in item_max_prob:
                    item_max_prob[token] = max(item_max_prob[token], val)
                else:
                    item_max_prob[token] = val

                p_itemset[token] = item_max_prob[token]

                if token not in new_item_freq:
                    new_item_freq[token] = 1
                else:
                    new_item_freq[token] += 1

                token = ""

                # Finished reading itemset
                if ch == "(":
                    p_seq.append(p_itemset)
                    u_seq.append(u_itemset)
            else:
                token += ch

        u_seq = u_seq[::-1]
        p_seq = p_seq[::-1]

        L = len(iu_SDB)
        last_index = -1 if L == 0 else iu_SDB[L - 1][0]
        iu_SDB.append((last_index + 1, u_seq))
        ip_SDB.append((last_index + 1, p_seq))
        L += 1

        if L > window_size:
            seq_index, u_seq = iu_SDB.popleft()
            ip_SDB.popleft()
            L -= 1

    # Assign weights of all items.
    # Using generated weights.
    WeightAssign.assign(wgt_file, item_weights, list(new_item_freq.keys()))
    # Manually. Assign only if not assigned before.
    # if not item_weights:
    #     WeightAssign.manual_assign(wgt_file, item_weights)

    for item_id, item_freq in new_item_freq.items():
        total_item_freq += item_freq
        total_item_weighted_freq += item_freq * item_weights[item_id]

    return (total_item_freq, total_item_weighted_freq)


class WeightAssign:
    current_point = 0

    @staticmethod
    def assign(
        wgt_file: IO[str], item_weights: WeightMap, item_ids: list[ItemID]
    ) -> None:
        wgt_file.seek(WeightAssign.current_point)
        for item_id in item_ids:
            if item_id not in item_weights:
                wgt_str = wgt_file.readline().strip()
                if wgt_str == "":
                    wgt_file.seek(0)
                    wgt_str = wgt_file.readline().strip()
                wgt = float(wgt_str)
                item_weights[item_id] = wgt
                WeightAssign.current_point = wgt_file.tell()

    @staticmethod
    def manual_assign(wgt_file: IO[str], item_weights: WeightMap) -> None:
        for line in wgt_file:
            item_id, wgt = line.split()
            item_weights[item_id] = float(wgt)

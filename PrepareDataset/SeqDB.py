import errno
import math
import os
import random
from typing import Optional


class SeqDatabase:
    # Class variable, shared to all instances
    dataset_ID: float = 0.0

    def __init__(self, input_file_name: Optional[str] = None) -> None:
        SeqDatabase.dataset_ID += 0.5
        # Number of sequences in the database
        self.sequence_count: int = 0
        # Maximum length of an itemset among all the sequences
        self.max_itemset_length: int = 0
        # Avg length of an itemset among all the itemsets in all the sequences
        self.avg_itemset_length: float = 0.0
        # All the distinct items present among all the sequences
        self.items: list[str] = []
        # Number of distinct items present among all the sequences
        self.item_count: int = 0
        # Lengths (#items) of the sequences
        self.sequence_lengths: list[int] = []
        # Avg length of a sequence
        self.avg_sequence_length: float = 0.0
        # Number of itemsets of the sequences
        self.itemset_counts: list[int] = []
        # Avg number of itemsets in a sequence
        self.avg_itemset_count: float = 0.0
        # Avg itemset lengths of the sequences
        self.avg_itemset_lengths: list[float] = []
        # Number of distinct items present in the sequences
        self.item_counts: list[int] = []
        # Avg number of distinct items present in the sequences
        self.avg_item_count: float = 0.0

        self.input_file_name: str
        if input_file_name is None:
            self.input_file_name = input("Enter input file name: ")
        else:
            self.input_file_name = input_file_name

        self.dataset_input_path_name = ""
        if self.input_file_name.endswith(".txt"):
            self.dataset_input_path_name = self.input_file_name[:-4]

        self.generate_statistics(self.input_file_name)

    def generate_statistics(self, input_file_name: str) -> None:
        with open(input_file_name, "r") as input_file:
            for line in input_file:
                # Remove -2, \n, \r as invalid values
                line = line.replace("-2", "").replace("\r", "").replace("\n", "")
                if line == "":
                    continue

                # We assume -1 as a separator for itemsets
                itemsets = line.split("-1")

                # All the distinct items in sequence
                sequence_items = []

                # All the lengths of the itemsets in the sequence
                sequence_itemset_lengths = []

                # Evaluate sequence_items, sequence_itemset_lengths,
                # and max_itemset_length
                for itemset_str in itemsets:
                    if itemset_str == " " or itemset_str == "":
                        break
                    itemset_str = itemset_str.strip()

                    itemset_items = itemset_str.split(" ")
                    itemset_length = 0

                    for item in itemset_items:
                        itemset_length += 1
                        if item not in self.items:
                            self.items.append(item)
                        if item not in sequence_items:
                            sequence_items.append(item)

                    sequence_itemset_lengths.append(itemset_length)
                    if itemset_length > self.max_itemset_length:
                        self.max_itemset_length = itemset_length

                # Update all the metrics
                self.sequence_lengths.append(sum(sequence_itemset_lengths))
                self.itemset_counts.append(len(sequence_itemset_lengths))
                self.avg_itemset_lengths.append(
                    sum(sequence_itemset_lengths) / len(sequence_itemset_lengths)
                )
                self.item_counts.append(len(sequence_items))

        # Update all the metrics
        self.item_count = len(self.items)
        self.sequence_count = len(self.sequence_lengths)
        self.avg_sequence_length = sum(self.sequence_lengths) / self.sequence_count
        self.avg_itemset_count = sum(self.itemset_counts) / self.sequence_count
        self.avg_itemset_length = sum(self.sequence_lengths) / sum(self.itemset_counts)
        self.avg_item_count = sum(self.item_counts) / self.sequence_count

    """
    Purpose: Probabilistically separates itemsets and makes sure that no two
        items in an itemset have the same item_id
    Parameters:
        same_itemset_probability: It should be in the range [1, 100].
            When a -1 is encountered in input_file, same_itemset_probability
            denotes the probability% that we continue reading the same itemset
        hash_bucket_size: The bucket size to use when hashing the items and
            assigning item_ids.
    """

    def convert_file(
        self, same_itemset_probability: float, hash_bucket_size: Optional[int] = None
    ) -> str:
        def generate_item_ids() -> dict[str, str]:
            item_ids: dict[str, str] = {}

            bucket_size: int
            if hash_bucket_size is None:
                bucket_size = int(
                    input("Enter converted itemset size (0 for no_change): ")
                )
            else:
                bucket_size = hash_bucket_size

            if bucket_size == 0:
                for i in self.items:
                    item_ids[i] = i
                return item_ids

            for i in self.items:
                item_id = hash(i) % bucket_size + 1
                item_ids[i] = str(item_id)

            return item_ids

        item_ids = generate_item_ids()

        output_filename = self.dataset_input_path_name + "_s.txt"
        output_file_location = f"../Files/datasets/{self.dataset_input_path_name}{str(same_itemset_probability)}/{output_filename}"
        if not os.path.exists(os.path.dirname(output_file_location)):
            try:
                os.makedirs(os.path.dirname(output_file_location))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        with open(self.input_file_name, "r") as input_file, open(
            output_file_location, "w+"
        ) as output_file:
            for line in input_file:
                line = line.replace("\r", "").replace("\n", "")
                if line == "":
                    continue
                tokens = line.split(" ")
                updated_tokens = []
                cur_itemset: list[str] = []

                for token in tokens:
                    if token == "-1":
                        p = random.randint(1, 100)
                        if p > same_itemset_probability:
                            # Start new itemset
                            updated_tokens.append(token)
                            cur_itemset.clear()
                    else:
                        if token == "-2":
                            updated_tokens.append(token)
                            continue

                        item_id = item_ids[token]
                        if item_id not in cur_itemset:
                            cur_itemset.append(item_id)
                            updated_tokens.append(item_id)
                        # Item already exists in current itemset,
                        # so start a new itemset from here
                        else:
                            updated_tokens.append("-1")
                            updated_tokens.append(item_id)
                            cur_itemset.clear()
                            cur_itemset.append(item_id)

                line = " ".join(updated_tokens)
                output_file.write(line)
                output_file.write("\n")

        return output_file_location

    def auto_partition(
        self, input_file_name: str, output_file_name: Optional[str] = None
    ) -> list[int]:
        partition_sizes: list[int] = []

        dataset_output_path_name = (
            "../Files/datasets/" + self.dataset_input_path_name.split("/")[2]
        )

        if output_file_name is None:
            output_file_name = dataset_output_path_name

        versions = ["v0", "v1", "v2", "v3"]

        def get_inc_size(version: str, db_size: int) -> int:
            r = db_size
            if version == "v0" or version == "v2":  # small inc
                low = math.floor(db_size * 0.05)
                high = math.floor(db_size * 0.10)
                r = int(random.randrange(low, high))
            else:  # large inc
                low = math.floor(db_size * 0.50)
                high = math.floor(db_size * 0.80)
                r = int(random.randrange(low, high))
            return r

        for version in versions:
            input_file = open(input_file_name, "r")
            output_file_path_name = (
                f"{dataset_output_path_name}/{version}/{output_file_name}"
            )

            print(f"__________For type__________{version}")

            partition_0_size: int
            if version == "v0" or version == "v1":  # small partition_0_size
                partition_0_size = math.floor(
                    self.sequence_count * 0.7
                )  # 50% of total uSDB
            else:  # small partition_0_size
                partition_0_size = math.floor(self.sequence_count * 0.8)

            print(f"Initial size (partition_0_size): {partition_0_size}")

            output_partition_path_name = f"{output_file_path_name}_partition_0.txt"

            if not os.path.exists(os.path.dirname(output_partition_path_name)):
                try:
                    os.makedirs(os.path.dirname(output_partition_path_name))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

            output_file = open(output_partition_path_name, "w+")
            for _ in range(0, partition_0_size):
                seq = input_file.readline()
                output_file.write(seq)
            output_file.close()

            rem_size = self.sequence_count - partition_0_size
            inc_count = 0
            while rem_size > 0:
                inc_count += 1
                inc_size = min(get_inc_size(version, partition_0_size), rem_size)
                rem_size -= inc_size
                if rem_size < 0.03 * partition_0_size:
                    inc_size += rem_size
                    rem_size = 0

                print(f"partition_{inc_count} size: {inc_size}")

                output_partition_path_name = (
                    f"{output_file_path_name}_partition_{inc_count}.txt"
                )

                output_file = open(output_partition_path_name, "w+")
                for _ in range(0, inc_size):
                    seq = input_file.readline()
                    output_file.write(seq)
                output_file.close()

            partition_sizes.append(inc_count)

            input_file.close()
            print("#_______________________________________________#")

        return partition_sizes

    def describe_dataset(self) -> str:
        def suggest_min_sup(avg_sequence_length: float, item_count: int) -> str:
            min_sup = round(avg_sequence_length * 100 / item_count, 3)
            return f"{min_sup} %"

        title = (
            "serial,"
            "input_file_name,"
            "sequence_count,"
            "avg_sequence_length,"
            "max_sequence_length,"
            "min_sequence_length,"
            "item_count,"
            "avg_item_count,"
            "max_item_count,"
            "min_item_count,"
            "avg_itemset_count,"
            "avg_itemset_length,"
            "max_itemset_length,"
            "suggested_min_sup"
        )
        result = (
            str(int(SeqDatabase.dataset_ID))
            + ","
            + self.input_file_name
            + ","
            + str(self.sequence_count)
            + ","
            + str(self.avg_sequence_length)
            + ","
            + str(max(self.sequence_lengths))
            + ","
            + str(min(self.sequence_lengths))
            + ","
            + str(self.item_count)
            + ","
            + str(self.avg_item_count)
            + ","
            + str(max(self.item_counts))
            + ","
            + str(min(self.item_counts))
            + ","
            + str(self.avg_itemset_count)
            + ","
            + str(self.avg_itemset_length)
            + ","
            + str(self.max_itemset_length)
            + ","
            + suggest_min_sup(self.avg_sequence_length, self.item_count)
        )

        heads = title.split(",")
        body = result.split(",")

        # print("_______________________________________________")
        for i in range(0, len(heads)):
            print(f"{heads[i]} : {body[i]}")

        print("*_______________________________________________*")

        return result

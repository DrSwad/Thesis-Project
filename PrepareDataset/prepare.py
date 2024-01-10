import errno
import os
from typing import IO

import SeqDB


def assign_probabilities(
    data_file: IO[str], probs_file: IO[str], where_to_write: IO[str]
) -> None:
    previous = probs_file.tell()

    for data in data_file:
        seq = "("
        token = ""

        for ch in data:
            if ch == " " or ch == "\n":
                if len(token) > 0:
                    value = int(token)
                    if value == -1:
                        seq = seq[: len(seq) - 1] + ")" + "("
                    elif value == -2:
                        if seq[len(seq) - 1] == "(":
                            seq = seq[: len(seq) - 1]
                        else:
                            seq = seq[: len(seq) - 1]
                            seq += ")"
                        where_to_write.write(seq)
                        where_to_write.write("\n")
                        break
                    else:
                        probs_file.seek(previous)
                        prb = probs_file.readline().strip()
                        if prb == "":
                            probs_file.seek(0)
                            prb = probs_file.readline().strip()
                        previous = probs_file.tell()
                        seq += f"{value}:{prb},"
                    token = ""
            else:
                token += ch
    where_to_write.close()


if __name__ == "__main__":
    datasets = [
        # "SIGN.txt"
        # "LEVIATHAN.txt",
        # "BIBLE.txt",
        "FIFA.txt",
        # "accidents_seq.txt",
        # "BMS2.txt",
    ]

    hash_bucket_sizes = [
        0,
        # 1000,
        # 1500,
        # 300,
        # 0,
        # 400,
    ]

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

    probs_file = open("../Files/probs.csv", "r")

    for same_itemset_probability in [50, 80]:
        print(
            "______________________Same Itemset Probability______________________",
            same_itemset_probability,
        )

        csv_file_name = (
            "../Files/datasets"
            + "/dataset_study_"
            + str(same_itemset_probability)
            + ".csv"
        )
        if not os.path.exists(os.path.dirname(csv_file_name)):
            try:
                os.makedirs(os.path.dirname(csv_file_name))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        csv_file = open(csv_file_name, "w+")
        csv_file.write(title)
        csv_file.write("\n")
        csv_file.close()

        for i in range(0, len(datasets)):
            csv_file = open(csv_file_name, "a")

            sdb = SeqDB.SeqDatabase(datasets[i])
            sdb.describe_dataset()

            converted_file_location = sdb.convert_file(
                same_itemset_probability, hash_bucket_sizes[i]
            )

            newSDB = SeqDB.SeqDatabase(converted_file_location)
            r = newSDB.describe_dataset()

            # Probability assign
            converted_file_location_with_prob = converted_file_location.replace(
                ".txt", "p.txt"
            )
            where_to_write = open(converted_file_location_with_prob, "w")
            data_file = open(converted_file_location, "r")
            assign_probabilities(data_file, probs_file, where_to_write)

            partition_sizes = newSDB.auto_partition(converted_file_location_with_prob)

            csv_file.write(r)
            csv_file.write("\n")
            csv_file.close()

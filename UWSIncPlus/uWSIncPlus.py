import time

from DataStructures.Trie import Trie
from FUWS.FUWSequence import FUWSequence
from Parameters.FileInfo import FileInfo
from Parameters.ProgramVariable import ProgramVariable
from Parameters.UserDefined import UserDefined
from Parameters.Variable import Variable
from Types.types import ExpectedSupport
from UtilityTechniques.DataPreProcessing import PreProcess
from UtilityTechniques.ProbabilityWeightAssign import WeightAssign
from UtilityTechniques.ThresholdCalculation import ThresholdCalculation
from UtilityTechniques.WAMCalculation import WAMCalculation


class uWSIncPlus:
    def __init__(
        self,
        input_database_file: str,
        input_increment_files: list[str],
        input_weight_file: str,
        output_directory: str,
    ) -> None:
        # Initialize file information where you wish to save the outputs of the algorithm
        FileInfo.set_initial_file_info(
            input_database_file,
            f"{output_directory}/fs.txt",
            f"{output_directory}/sfs.txt",
            f"{output_directory}/pfs.txt",
        )
        FileInfo.ls = open(f"{output_directory}/ls.txt", "w")
        FileInfo.time_info = open(f"{output_directory}/time_info_plus_v0.txt", "w")
        assert FileInfo.initial_dataset is not None
        assert FileInfo.fs is not None
        assert FileInfo.sfs is not None
        assert FileInfo.pfs is not None

        # Preprocess dataset in the way that is described in our algorithm
        PreProcess().read_and_process_input_database()

        # Assign weights of all items

        # WeightAssign.assign(ProgramVariable.itemList)  # using generated weights
        WeightAssign.manual_assign(input_weight_file)  # manually

        # WAM will be calculated && DataBase size will be been updated

        WAMCalculation.update_WAM()
        Variable.size_of_dataset = len(ProgramVariable.uSDB)

        previous_time = time.time()

        # Run FUWS algorithm to get FS and SFS from initial datasets and store store them into USeq-Trie
        self.fssfs_trie = FUWSequence().generate_trie_of_actual_sequences()
        self.fssfs_trie.only_keep_semi_frequent_nodes()

        self.fssfs_trie.log_semi_frequent_nodes_in_trie(
            FileInfo.fs, ThresholdCalculation.get_wgt_exp_sup()
        )
        self.fssfs_trie.log_semi_frequent_nodes_in_trie(
            FileInfo.sfs,
            ThresholdCalculation.get_semi_wgt_exp_sup(),
            ThresholdCalculation.get_wgt_exp_sup(),
        )

        cur_time = time.time()
        FileInfo.time_info.write(str(cur_time - previous_time))
        FileInfo.time_info.write("\n")

        FileInfo.fs.write("-----------\n")
        FileInfo.sfs.write("-----------\n")
        FileInfo.pfs.write("-----------\n")
        FileInfo.ls.write("-----------\n")

        for input_increment_file in input_increment_files:
            FileInfo.initial_dataset = open(input_increment_file, "r")
            PreProcess().read_and_process_input_database()

            # WeightAssign.assign(ProgramVariable.itemList)
            WeightAssign.manual_assign(input_weight_file)

            prev_upto_sum = WAMCalculation.upto_sum
            prev_upto_wSum = WAMCalculation.upto_wSum
            WAMCalculation.upto_wSum = 0.0
            WAMCalculation.upto_sum = 0

            WAMCalculation.update_WAM()

            WAMCalculation.upto_wSum += prev_upto_wSum
            WAMCalculation.upto_sum += prev_upto_sum

            previous_time = time.time()
            self.uWSIncPlusMethod(UserDefined.min_sup * 2)

            cur_time = time.time()
            FileInfo.time_info.write(str(cur_time - previous_time))
            FileInfo.time_info.write("\n")

            FileInfo.fs.write("-----------\n")
            FileInfo.sfs.write("-----------\n")
            FileInfo.pfs.write("-----------\n")
            FileInfo.ls.write("-----------\n")

    def uWSIncPlusMethod(self, local_min_sup: ExpectedSupport) -> None:
        # Save the threshold and the size of the dataset to trie trie for only the incremental dataset
        prev_min_sup = UserDefined.min_sup
        prev_size_of_dataset = Variable.size_of_dataset

        # Set the min_sup to the given local_min_sup
        UserDefined.min_sup = local_min_sup
        Variable.size_of_dataset = len(ProgramVariable.uSDB)

        self.cur_ls_trie = FUWSequence().generate_trie_of_actual_sequences()
        self.cur_ls_trie.log_semi_frequent_nodes_in_trie(FileInfo.ls)

        for i in range(0, len(ProgramVariable.uSDB)):
            self.fssfs_trie.actual_support_calculation(i)

        # Merging tries, keeping the PFS nodes
        self.fssfs_trie.merge_ls_with_fssfs_trie(
            self.cur_ls_trie.root_node, self.fssfs_trie.root_node
        )

        # Update tries, keeping the PFS nodes
        self.fssfs_trie.evaluate_semi_frequency_flags(self.fssfs_trie.root_node)
        self.fssfs_trie.only_keep_semi_frequent_nodes()

        # Since the PFS nodes are already in the trie, it's safe to update the threshold now
        pfs_semi_threshold = ThresholdCalculation.get_semi_wgt_exp_sup()
        UserDefined.min_sup = prev_min_sup
        Variable.size_of_dataset = prev_size_of_dataset + len(ProgramVariable.uSDB)
        Variable.WAM = WAMCalculation.upto_wSum / WAMCalculation.upto_sum

        # Writing tries to file
        self.fssfs_trie.log_semi_frequent_nodes_in_trie(
            FileInfo.pfs,
            pfs_semi_threshold,
            ThresholdCalculation.get_semi_wgt_exp_sup(),
        )
        self.fssfs_trie.log_semi_frequent_nodes_in_trie(
            FileInfo.fs, ThresholdCalculation.get_wgt_exp_sup()
        )
        self.fssfs_trie.log_semi_frequent_nodes_in_trie(
            FileInfo.sfs,
            ThresholdCalculation.get_semi_wgt_exp_sup(),
            ThresholdCalculation.get_wgt_exp_sup(),
        )

        return

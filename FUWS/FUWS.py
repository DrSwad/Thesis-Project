import time

from DataStructures.Trie import Trie
from FUWS.FUWSequence import FUWSequence
from Parameters.FileInfo import FileInfo
from Parameters.ProgramVariable import ProgramVariable
from Parameters.Variable import Variable
from UtilityTechniques.DataPreProcessing import PreProcess
from UtilityTechniques.ProbabilityWeightAssign import WeightAssign
from UtilityTechniques.ThresholdCalculation import ThresholdCalculation
from UtilityTechniques.WAMCalculation import WAMCalculation


class FUWS:
    def __init__(
        self,
        input_database_file: str,
        input_weight_file: str,
        output_directory: str,
    ) -> None:
        FileInfo.initial_dataset = open(input_database_file, "r")
        FileInfo.fs = open(f"{output_directory}/fs.txt", "w")
        FileInfo.sfs = open(f"{output_directory}/sfs.txt", "w")

        # Preprocess dataset in the way that is described in our algorithm
        PreProcess().read_and_process_input_database()

        # Assign weights of all items
        # Using generated weights
        WeightAssign.assign(input_weight_file, ProgramVariable.item_list)
        # Manually
        # WeightAssign.manual_assign(input_weight_file)

        # WAM will be calculated && DataBase size will be been updated

        WAMCalculation.update_WAM()
        Variable.size_of_dataset = len(ProgramVariable.uSDB)

        start_time = time.time()

        # Find the frequent and semi-frequent patterns
        fssfs_trie = FUWSequence().generate_trie_of_actual_sequences()

        # Remove false patterns using the calculated weighted-support values
        fssfs_trie.only_keep_semi_frequent_nodes()

        end_time = time.time()

        # Write the desired patterns (FS & SFS) into files
        fssfs_trie.log_trie(FileInfo.fs, ThresholdCalculation.get_wgt_exp_sup())
        fssfs_trie.log_trie(
            FileInfo.sfs,
            ThresholdCalculation.get_semi_wgt_exp_sup(),
            ThresholdCalculation.get_wgt_exp_sup(),
        )

        print("Total required time(in Seconds): ", end_time - start_time)

        FileInfo.initial_dataset.close()
        FileInfo.fs.close()
        FileInfo.sfs.close()

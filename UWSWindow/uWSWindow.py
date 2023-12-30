import time

from FUWS.IncrementalFUWSequence import IncrementalFUWSequence
from Parameters.FileInfo import FileInfo
from Parameters.ProgramVariable import ProgramVariable
from Parameters.Variable import Variable
from UtilityTechniques.DataPreProcessing import PreProcess
from UtilityTechniques.ProbabilityWeightAssign import WeightAssign
from UtilityTechniques.ThresholdCalculation import ThresholdCalculation
from UtilityTechniques.WAMCalculation import WAMCalculation


class uWSWindow:
    def __init__(
        self,
        input_database_file: str,
        input_increment_files: list[str],
        input_weight_file: str,
        output_directory: str,
        window_size: int,
    ) -> None:
        # Initialize file information where you wish to save the outputs of the algorithm
        FileInfo.fs = open(f"{output_directory}/fs.txt", "w")
        FileInfo.sfs = open(f"{output_directory}/sfs.txt", "w")
        FileInfo.time_info = open(f"{output_directory}/time_info_plus_v0.txt", "w")

        # Maximum amount of data to store in the database, when new sequences exceed this limit,
        # old sequences are removed
        self.window_size = window_size

        # Load initial data
        FileInfo.initial_dataset = open(input_database_file, "r")

        # Assign weights of all items
        # WeightAssign.assign(ProgramVariable.itemList)  # using generated weights
        WeightAssign.manual_assign(input_weight_file)  # manually

        self.process_new_data()

        for input_increment_file in input_increment_files:
            # Load incremental data
            FileInfo.initial_dataset = open(input_increment_file, "r")

            # WeightAssign.assign(ProgramVariable.itemList)  # using generated weights
            WeightAssign.manual_assign(input_weight_file)  # manually

            self.process_new_data()

        FileInfo.initial_dataset.close()
        FileInfo.fs.close()
        FileInfo.sfs.close()
        FileInfo.time_info.close()

    def process_new_data(self) -> None:
        # Preprocess dataset in the way that is described in our algorithm
        PreProcess().read_and_process_input_database()

        # Add the data into iuSDB and ipSDB
        self.load_data_into_incremental_database()

        # WAM will be calculated and database size will be been updated
        WAMCalculation.update_WAM()
        Variable.size_of_dataset = len(ProgramVariable.uSDB)

        previous_time = time.time()

        # TODO
        # Run FUWS algorithm to get FS and SFS from initial datasets and store store them into USeq-Trie
        # self.fssfs_trie = IncrementalFUWSequence().generate_trie()

        # Log answers into file
        assert FileInfo.fs is not None
        assert FileInfo.sfs is not None
        self.fssfs_trie.log_trie(FileInfo.fs, ThresholdCalculation.get_wgt_exp_sup())
        self.fssfs_trie.log_trie(
            FileInfo.sfs,
            ThresholdCalculation.get_semi_wgt_exp_sup(),
            ThresholdCalculation.get_wgt_exp_sup(),
        )

        # Log time
        cur_time = time.time()
        assert FileInfo.time_info is not None
        FileInfo.time_info.write(str(cur_time - previous_time))
        FileInfo.time_info.write("\n")

    def load_data_into_incremental_database(self) -> None:
        for u_seq, p_seq in zip(ProgramVariable.uSDB, ProgramVariable.pSDB):
            L = len(ProgramVariable.iuSDB)
            last_index = -1 if L == 0 else ProgramVariable.iuSDB[L - 1][0]
            ProgramVariable.iuSDB.append((last_index + 1, u_seq))
            ProgramVariable.ipSDB.append((last_index + 1, p_seq))
            L += 1

            while L >= self.window_size:
                ProgramVariable.iuSDB.popleft()
                ProgramVariable.ipSDB.popleft()
                L -= 1

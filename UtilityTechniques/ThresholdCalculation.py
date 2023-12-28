from Parameters.UserDefined import UserDefined
from Parameters.Variable import Variable


class ThresholdCalculation:
    @staticmethod
    def get_minExpSup() -> float:
        return UserDefined.min_sup * Variable.size_of_dataset

    @staticmethod
    def get_semi_threshold() -> float:
        return ThresholdCalculation.get_minExpSup() * Variable.mu

    @staticmethod
    def get_local_threshold() -> float:
        return (
            UserDefined.min_sup
            * (
                Variable.window_size * Variable.size_of_increment
                + Variable.size_of_dataset
            )
        ) / (Variable.window_size * Variable.size_of_increment)

    @staticmethod
    def get_minExpWgtSup() -> float:
        return Variable.WAM * Variable.size_of_dataset * UserDefined.wgt_factor

    @staticmethod
    def update_dataset(sz: int) -> None:
        Variable.size_of_dataset += sz

    @staticmethod
    def get_wgt_exp_sup() -> float:
        return (
            UserDefined.min_sup
            * Variable.size_of_dataset
            * UserDefined.wgt_factor
            * Variable.WAM
        )

    @staticmethod
    def get_semi_wgt_exp_sup() -> float:
        return ThresholdCalculation.get_wgt_exp_sup() * Variable.mu

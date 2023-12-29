from Parameters.UserDefined import UserDefined
from Parameters.Variable import Variable


class ThresholdCalculation:
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

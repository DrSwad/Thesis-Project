from Parameters.ProgramVariable import ProgramVariable
from Parameters.Variable import Variable


class WAMCalculation:
    upto_wSum = 0.0
    upto_sum = 0

    @staticmethod
    def update_WAM() -> None:
        for item_id in ProgramVariable.cnt_dic:
            wgt = ProgramVariable.wgt_dic.get(item_id)
            assert wgt is not None

            cnt = ProgramVariable.cnt_dic.get(item_id)
            assert cnt is not None

            WAMCalculation.upto_sum += cnt
            WAMCalculation.upto_wSum += cnt * wgt

        Variable.WAM = WAMCalculation.upto_wSum / WAMCalculation.upto_sum

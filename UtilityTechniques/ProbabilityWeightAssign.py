from io import TextIOWrapper
from typing import Optional

from Parameters.ProgramVariable import ProgramVariable
from Types.types import ItemID


class WeightAssign:
    wgt_file: Optional[TextIOWrapper] = None
    current_point = 0

    @staticmethod
    def assign(input_weight_file: str, item_ids: list[ItemID]) -> None:
        if WeightAssign.wgt_file is None:
            WeightAssign.wgt_file = open(input_weight_file, "r")
        WeightAssign.wgt_file.seek(WeightAssign.current_point)
        for item_id in item_ids:
            if item_id not in ProgramVariable.wgt_dic:
                wgt_str = WeightAssign.wgt_file.readline().strip()
                if wgt_str == "":
                    WeightAssign.wgt_file.seek(0)
                    wgt_str = WeightAssign.wgt_file.readline().strip()
                wgt = float(wgt_str)
                ProgramVariable.wgt_dic[item_id] = wgt
                WeightAssign.current_point = WeightAssign.wgt_file.tell()

    @staticmethod
    def manual_assign(input_weight_file: str) -> None:
        wgt_file = open(input_weight_file, "r")
        for item_id in wgt_file:
            item_id, wgt = item_id.split()
            ProgramVariable.wgt_dic[item_id] = float(wgt)

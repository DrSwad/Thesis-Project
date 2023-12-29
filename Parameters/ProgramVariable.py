from Types.types import ItemID, UDatabase, WeightMap


class ProgramVariable:
    uSDB: UDatabase = list()
    pSDB: UDatabase = list()
    item_list: list[ItemID] = list()
    cnt_dic: dict[ItemID, int] = dict()
    wgt_dic: WeightMap = dict()

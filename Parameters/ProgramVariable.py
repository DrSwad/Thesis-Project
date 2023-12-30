from collections import deque

from Types.types import ItemID, IUDatabase, UDatabase, WeightMap


class ProgramVariable:
    uSDB: UDatabase = list()
    pSDB: UDatabase = list()
    iuSDB: IUDatabase = deque()
    ipSDB: IUDatabase = deque()
    item_list: list[ItemID] = list()
    cnt_dic: dict[ItemID, int] = dict()
    wgt_dic: WeightMap = dict()

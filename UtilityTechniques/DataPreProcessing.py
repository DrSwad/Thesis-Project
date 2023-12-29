from typing import cast

from sortedcontainers import SortedDict

from Parameters.FileInfo import FileInfo
from Parameters.ProgramVariable import ProgramVariable
from Types.types import ItemID, ItemProbability, UItemset, USequence


class PreProcess:
    def __init__(self) -> None:
        ProgramVariable.uSDB = []
        ProgramVariable.pSDB = []
        ProgramVariable.item_list = list()
        ProgramVariable.cnt_dic = dict()

    def read_and_process_input_database(self) -> None:
        assert FileInfo.initial_dataset is not None
        for seq in FileInfo.initial_dataset:
            pSeq: USequence = []
            uSeq: USequence = []
            rseq = seq[::-1]

            tnewSeqList: UItemset = SortedDict()
            item: ItemID = ""
            val: ItemProbability = 0.0
            seqMap: dict[ItemID, ItemProbability] = dict()

            uItemSet: UItemset = SortedDict()

            for ch in rseq:
                if ch == " ":
                    ch = ""
                elif ch == ")":
                    tnewSeqList = SortedDict()
                    uItemSet = SortedDict()
                elif ch == ":":
                    item = item.strip()
                    item = item[::-1]
                    item = item.strip()
                    if len(item) == 0:
                        item = "0"
                    val = float(item)
                    item = ""
                elif ch == ",":
                    item = item[::-1]
                    uItemSet[item] = val
                    if item in seqMap:
                        seqMap[item] = max(seqMap[item], val)
                    else:
                        seqMap[item] = val

                    val = seqMap[item]
                    tnewSeqList[item] = val

                    if item not in ProgramVariable.item_list:
                        ProgramVariable.item_list.append(str(item))
                    if item not in ProgramVariable.cnt_dic:
                        ProgramVariable.cnt_dic[item] = 1
                    else:
                        ProgramVariable.cnt_dic[item] += 1

                    item = ""
                elif ch == "(":
                    item = item[::-1]
                    if item in seqMap:
                        seqMap[item] = max(seqMap[item], val)
                    else:
                        seqMap[item] = val

                    if item not in ProgramVariable.item_list:
                        ProgramVariable.item_list.append(str(item))
                    if item not in ProgramVariable.cnt_dic:
                        ProgramVariable.cnt_dic[item] = 1
                    else:
                        ProgramVariable.cnt_dic[item] += 1

                    uItemSet[item] = val
                    val = seqMap[item]
                    tnewSeqList[item] = val

                    pSeq.append(tnewSeqList)
                    uSeq.append(uItemSet)

                    item = ""
                else:
                    item += ch

            ProgramVariable.uSDB.append(uSeq[::-1])
            ProgramVariable.pSDB.append(pSeq[::-1])
        return

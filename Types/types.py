from enum import Enum
from typing import TypeAlias

from sortedcontainers import SortedDict, SortedList

ItemID: TypeAlias = str
ItemProbability: TypeAlias = float
ItemWeight: TypeAlias = float
ExpectedSupport: TypeAlias = float
WeightedExpectedSupport: TypeAlias = float
UItem: TypeAlias = tuple[ItemID, ItemProbability]
Itemset: TypeAlias = SortedList[ItemID]  # type: ignore
UItemset: TypeAlias = SortedDict[ItemID, ItemProbability]  # type: ignore
USequence: TypeAlias = list[UItemset]
UDatabase: TypeAlias = list[USequence]
WeightMap: TypeAlias = dict[ItemID, ItemWeight]


class ExtensionType(Enum):
    s = "S"
    i = "I"
    none = "None"


class ProjectionPosition:
    def __init__(
        self,
        seq_index: int,
        set_index: int,
        item_id: ItemID,
    ) -> None:
        self.seq_index = seq_index
        self.set_index = set_index
        self.item_id = item_id

    def __repr__(self) -> str:
        return f"P[{self.seq_index}, {self.set_index}, {self.item_id}]"

    def __str__(self) -> str:
        return f"P[{self.seq_index}, {self.set_index}, {self.item_id}]"


ProjectedDatabase: TypeAlias = list[ProjectionPosition]

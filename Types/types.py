from enum import Enum
from typing import Deque, TypeAlias

from sortedcontainers import SortedDict, SortedList

ItemID: TypeAlias = str
ItemProbability: TypeAlias = float
ItemWeight: TypeAlias = float
UItem: TypeAlias = tuple[ItemID, ItemProbability]

ExpectedSupport: TypeAlias = float
WeightedExpectedSupport: TypeAlias = float
WeightMap: TypeAlias = dict[ItemID, ItemWeight]

Itemset: TypeAlias = SortedList[ItemID]  # type: ignore
UItemset: TypeAlias = SortedDict[ItemID, ItemProbability]  # type: ignore

USequence: TypeAlias = list[UItemset]
IUSequence: TypeAlias = tuple[int, USequence]

UDatabase: TypeAlias = list[USequence]
IUDatabase: TypeAlias = Deque[IUSequence]


class ExtensionType(Enum):
    s = "S"
    i = "I"
    none = "None"


SequenceIndex: TypeAlias = int
SetIndex: TypeAlias = int
Edge: TypeAlias = tuple[ItemID, ExtensionType]


class ProjectionPosition:
    def __init__(
        self,
        seq_index: SequenceIndex,
        set_index: SetIndex,
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
IProjectedDatabase: TypeAlias = SortedDict[SequenceIndex, SetIndex]  # type: ignore

MaxProbDP: TypeAlias = SortedDict[SequenceIndex, ItemProbability]  # type: ignore
CapDP: TypeAlias = SortedDict[SequenceIndex, WeightedExpectedSupport]  # type: ignore
ActualDP: TypeAlias = SortedDict[SequenceIndex, list[tuple[SetIndex, ItemProbability]]]  # type: ignore

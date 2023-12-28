from Types.types import ExpectedSupport, ItemWeight


class UserDefined:
    min_sup: ExpectedSupport = 0.0
    wgt_factor: ItemWeight = 0.0

    @staticmethod
    def __init__(ms: ExpectedSupport, wf: ItemWeight) -> None:
        UserDefined.min_sup = ms
        UserDefined.wgt_factor = wf

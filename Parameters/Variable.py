class Variable:
    local_threshold = 0.0
    window_size = 0.0
    mu = 0.0
    WAM = 0.0
    size_of_dataset: int = 0
    size_of_increment: int = 0
    eps = 0.000000001

    @staticmethod
    def __init__(
        local_threshold: float, window_size: float, mu: float, wam: float
    ) -> None:
        Variable.local_threshold = local_threshold
        Variable.window_size = window_size
        Variable.mu = mu
        Variable.WAM = wam
        pass

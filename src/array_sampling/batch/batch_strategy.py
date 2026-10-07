from enum import Enum


class BatchStrategy(Enum):
    """How a batch of index samples is drawn.

    Attributes
    ----------
    VECTORISED
        Draw one index for every row per step, ``count`` NumPy steps in total.
        Each step compares against the indices already chosen, so the cost is
        ``O(B * count**2)`` element operations with little Python overhead.
        Fastest for small ``count``.
    PER_ROW
        Call ``numpy.random.Generator.choice`` once per row. The cost is
        ``O(B * count)`` plus one Python round trip per row, which wins once
        ``count`` is large.
    """

    VECTORISED = "vectorised"
    PER_ROW = "per_row"

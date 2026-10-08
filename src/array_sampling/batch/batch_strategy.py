from enum import Enum


class BatchStrategy(Enum):
    """How a batch of index samples is drawn.

    Attributes
    ----------
    AUTOMATIC
        Pick ``VECTORISED`` or ``PER_ROW`` per call from an estimate of their
        running times, which depends on both the batch size and ``count``.
    VECTORISED
        Draw one index for every row per step, ``count`` NumPy steps in total.
        Each step compares against the indices already chosen, so the cost is
        about ``count**2`` NumPy calls touching ``B`` elements each. Fastest
        for large batches with small ``count``.
    PER_ROW
        Call ``numpy.random.Generator.choice`` once per row. The cost is
        ``O(B * count)`` plus one Python round trip per row, which wins for
        small batches or large ``count``.
    """

    AUTOMATIC = "automatic"
    VECTORISED = "vectorised"
    PER_ROW = "per_row"

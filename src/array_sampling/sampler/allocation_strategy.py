from enum import Enum


class AllocationStrategy(Enum):
    """Rule that splits a total sample size across strata.

    Attributes
    ----------
    PROPORTIONAL
        Each stratum receives a share proportional to its size.
    EQUAL
        Every stratum receives the same share.
    """

    PROPORTIONAL = "proportional"
    EQUAL = "equal"

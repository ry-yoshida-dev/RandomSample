from enum import Enum


class ReplacementMode(Enum):
    """Whether an element may be selected more than once.

    The names follow the standard abbreviations of survey sampling theory:
    SWOR (sampling without replacement) and SWR (sampling with replacement).
    Conceptually, each draw takes a ball out of an urn; the mode decides
    whether the ball is put back before the next draw.

    Attributes
    ----------
    SWOR
        Sampling without replacement. A drawn element is never drawn again,
        so the sample contains each population position at most once and the
        sample size cannot exceed the population size. This is the default
        of every sampler and matches typical use cases such as selecting
        survey respondents or holding out evaluation rows. Equivalent to
        ``random.sample`` or ``numpy.random.choice(..., replace=False)``.
    SWR
        Sampling with replacement. Every draw is independent of the previous
        ones, so the same position may appear multiple times and the sample
        size may exceed the population size (for example
        ``SampleFraction(2.0)``). Used for bootstrap resampling and
        weight-driven simulations. Equivalent to ``random.choices`` or
        ``numpy.random.choice(..., replace=True)``.
    """

    SWOR = "swor"
    SWR = "swr"

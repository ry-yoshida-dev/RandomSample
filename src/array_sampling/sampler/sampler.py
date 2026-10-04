from abc import ABC, abstractmethod

from array_sampling.internal.random_access_array import RandomAccessArray
from array_sampling.random_generator import RandomGenerator
from array_sampling.sample_result import SampleResult


class Sampler[T](ABC):
    """Common interface of every sampler.

    A sampler is configured once through its constructor and then draws a
    sample from any population passed to ``sample``, so samplers are
    interchangeable wherever a ``Sampler[T]`` is expected.

    Parameters
    ----------
    random_generator : RandomGenerator | None
        Random number generator. A non-deterministic one is created when omitted.
    """

    def __init__(self, random_generator: RandomGenerator | None = None) -> None:
        self._random_generator: RandomGenerator = (
            random_generator if random_generator is not None else RandomGenerator()
        )

    @abstractmethod
    def sample(self, population: RandomAccessArray[T]) -> SampleResult[T]:
        """Draw a sample from a population.

        Parameters
        ----------
        population : RandomAccessArray[T]
            Population to sample from.

        Returns
        -------
        SampleResult[T]
            Selected elements with their zero-based positions in ``population``.
        """

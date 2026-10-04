from abc import ABC, abstractmethod


class SampleSize(ABC):
    """Specification of how many elements to draw from a population."""

    @abstractmethod
    def resolve(self, population_size: int) -> int:
        """Convert the specification into a concrete element count.

        Parameters
        ----------
        population_size : int
            Number of elements in the population.

        Returns
        -------
        int
            Number of elements to draw.
        """

import math
from random import Random
from typing import Self


class RandomGenerator:
    """Injectable random number generator shared by all samplers.

    Parameters
    ----------
    backend : Random | None
        Underlying ``random.Random`` instance. One seeded from system entropy is
        created when omitted.
    """

    def __init__(self, backend: Random | None = None) -> None:
        self._backend: Random = backend if backend is not None else Random()

    @classmethod
    def from_seed(cls, seed: int) -> Self:
        """Create a reproducible generator.

        Parameters
        ----------
        seed : int
            Seed passed to ``random.Random``.

        Returns
        -------
        Self
            Deterministic random generator.
        """
        return cls(Random(seed))

    @property
    def backend(self) -> Random:
        """Underlying ``random.Random`` instance."""
        return self._backend

    def open_unit_interval(self) -> float:
        """Draw a uniform value strictly inside ``(0, 1)``.

        Returns
        -------
        float
            Uniform value that is safe to pass to ``math.log``.
        """
        value: float = self._backend.random()
        while value == 0.0:
            value = self._backend.random()
        return value

    def weighted_key(self, weight: float) -> float:
        """Draw an Efraimidis-Spirakis priority key in log space.

        Keeping the ``k`` largest keys yields a weighted sample without
        replacement. The log form avoids the underflow of ``u ** (1 / w)``.

        Parameters
        ----------
        weight : float
            Strictly positive weight.

        Returns
        -------
        float
            Non-positive key; larger keys win.
        """
        return math.log(self.open_unit_interval()) / weight

    def random_index(self, size: int) -> int:
        """Draw a uniform integer from ``range(size)``.

        Parameters
        ----------
        size : int
            Strictly positive upper bound.

        Returns
        -------
        int
            Uniform index.
        """
        return self._backend.randrange(size)

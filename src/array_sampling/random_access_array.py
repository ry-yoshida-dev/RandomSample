from collections.abc import Iterator
from typing import Protocol


class RandomAccessArray[T](Protocol):
    """Minimal read-only array interface required by every sampler.

    ``list``, ``tuple``, ``range``, and lazily loaded containers that
    implement ``__len__``, integer ``__getitem__``, and ``__iter__`` all
    satisfy it, so large arrays never have to be copied into memory to be
    sampled.
    """

    def __len__(self) -> int: ...

    def __getitem__(self, index: int, /) -> T: ...

    def __iter__(self) -> Iterator[T]: ...

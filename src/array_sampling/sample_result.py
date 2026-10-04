from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SampleResult[T]:
    """Selected elements together with their positions in the source.

    Parameters
    ----------
    items : tuple[T, ...]
        Selected elements.
    indices : tuple[int, ...]
        Zero-based positions of ``items`` in the source array or stream,
        aligned one-to-one with ``items``.
    """

    items: tuple[T, ...]
    indices: tuple[int, ...]

    def __post_init__(self) -> None:
        if len(self.items) != len(self.indices):
            raise ValueError(
                "items and indices must have the same length, "
                + f"got {len(self.items)} and {len(self.indices)}."
            )

    def __len__(self) -> int:
        return len(self.items)

# array-sampling

## Overview

Practical, dependency-free sampling utilities for arrays and streams.

- **Basic extraction**: uniform or weighted sampling, with or without
  replacement, sized by absolute count or by fraction.
- **Large data and streams**: index-only sampling of lazy arrays and
  single-pass reservoir / Bernoulli sampling with bounded memory.
- **Production features**: stratified sampling with allocation strategies,
  per-stratum quotas, reproducible seeding, and a fail-fast error hierarchy.

Requires Python 3.12+.

## Choosing a sampler

| Situation | Sampler | Memory |
| --- | --- | --- |
| Array in memory or lazily indexable | `ArraySampler` | `O(k)` uniform, `O(n)` weighted |
| Stream, fixed sample size | `ReservoirSampler` | `O(k)` |
| Stream, fixed size, weighted | `WeightedReservoirSampler` | `O(k)` |
| Stream, fixed rate | `BernoulliSampler` | `O(1)` with `stream` |
| Groups must be represented | `StratifiedSampler` | `O(n)` indices |
| Explicit size per group | `QuotaSampler` | `O(n)` indices |
| Many small index samples at once (NumPy) | `array_sampling.batch.BatchIndexSampler` | `O(Bk²)` for small `k`, else `O(Bk)` |

`array_sampling.batch` requires the `numpy` extra: `pip install "array-sampling[numpy]"`.

## Examples

Every sampler derives from `Sampler[T]`: it is configured once in its
constructor and `sample(population)` returns a `SampleResult[T]`, so samplers
are interchangeable.

```python
from array_sampling import (
    ArraySampler,
    RandomGenerator,
    ReplacementMode,
    ReservoirSampler,
    SampleCount,
    SampleFraction,
    Sampler,
    SamplingError,
    StratifiedSampler,
)

random_generator = RandomGenerator.from_seed(42)

uniform: ArraySampler[int] = ArraySampler(SampleCount(10), random_generator=random_generator)
uniform.sample(range(1_000))

weights = {"a": 5.0, "b": 1.0, "c": 1.0}
ArraySampler(SampleCount(2), weight_of=weights.__getitem__).sample(["a", "b", "c"])

bootstrap: ArraySampler[str] = ArraySampler(SampleFraction(1.0), replacement=ReplacementMode.SWR)
bootstrap.sample(["a", "b", "c"])

reservoir: ReservoirSampler[int] = ReservoirSampler(100, random_generator)
reservoir.sample(range(10_000_000)).items

records = [("free", 1), ("free", 2), ("pro", 3), ("pro", 4)]
by_plan: Sampler[tuple[str, int]] = StratifiedSampler(lambda record: record[0], SampleCount(2))
by_plan.sample(records)

try:
    uniform.sample([1, 2])
except SamplingError as error:
    print(error)
```

## Development

```bash
uv sync
uv run pytest
uv run mypy
uv run basedpyright
uv run ruff check .
```

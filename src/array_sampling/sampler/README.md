# sampler

## Overview

Sampling algorithms. Every sampler derives from `Sampler[T]`: all settings
(size, replacement, weights, strata) are passed to the constructor, and
`sample(population)` returns a `SampleResult[T]` whose `indices` are positions
in `population`. Samplers are therefore interchangeable wherever a
`Sampler[T]` is expected.

**Array sampling** (`ArraySampler`) works on arrays whose length is known and
whose elements are accessible by integer index. Indices are drawn first and
elements are fetched afterwards, so lazy containers (memory-mapped files,
`range`, database-backed sequences) are never fully loaded for uniform
sampling. Weighted sampling evaluates `weight_of` on every element.

| Mode | Uniform | Weighted |
| --- | --- | --- |
| Without replacement | `random.sample` over `range(n)`, `O(k)` memory | Efraimidis-Spirakis keys + top-k heap, `O(n log k)` |
| With replacement | `randrange` per draw, `O(k)` memory | `random.choices` with cumulative weights, `O(n + k log n)` |

**Streaming sampling** consumes any iterable in a single pass.

| Sampler | Use case | Memory |
| --- | --- | --- |
| `ReservoirSampler` | Fixed-size uniform sample (Algorithm L) | `O(k)` |
| `WeightedReservoirSampler` | Fixed-size weighted sample without replacement (A-Res) | `O(k)` |
| `BernoulliSampler` | Fixed inclusion rate; `stream` yields lazily | `O(1)` with `stream` |

When elements arrive one at a time, use `UniformReservoir` / `WeightedReservoir`
from [reservoir/](../reservoir/README.md) directly with `add`, `extend`, and
`result`.

**Stratified sampling** groups elements by a label function and returns a
`StratifiedSampleResult`, a `SampleResult` that also keeps the per-stratum
breakdown.

- `StratifiedSampler` splits a total size across strata. Counts always sum
  to the total (largest remainder rounding); without replacement, a stratum
  never receives more than its size and the overflow is redistributed.
  `minimum_per_stratum` protects small strata from receiving zero elements.
- `QuotaSampler` draws an explicit size from each stratum, resolved against
  that stratum's size.

## Components

| Component | Responsibility |
| --- | --- |
| [sampler.py](sampler.py) | Abstract base class shared by every sampler. |
| [samplers/](samplers/README.md) | Concrete `Sampler` subclasses. |
| [stratum_allocator.py](stratum_allocator.py) | Splits a total into per-stratum counts. |
| [allocation_strategy.py](allocation_strategy.py) | `PROPORTIONAL` / `EQUAL` allocation rules. |

## Examples

```python
from array_sampling import (
    ArraySampler,
    BernoulliSampler,
    QuotaSampler,
    RandomGenerator,
    SampleCount,
    SampleFraction,
    Sampler,
    StratifiedSampler,
    UniformReservoir,
)

random_generator = RandomGenerator.from_seed(42)

samplers: list[Sampler[int]] = [
    ArraySampler(SampleCount(5), random_generator=random_generator),
    BernoulliSampler(0.01, random_generator),
]
results = [sampler.sample(range(10_000)) for sampler in samplers]

one_percent = BernoulliSampler[int](0.01).stream(range(10**9))

reservoir: UniformReservoir[str] = UniformReservoir(100, random_generator)
with open("access.log") as lines:
    reservoir.extend(lines)
reservoir.result().items


def plan_of(user: tuple[int, str]) -> str:
    return user[1]


users = [(1, "free"), (2, "pro")]
StratifiedSampler(plan_of, SampleCount(2), minimum_per_stratum=1).sample(users)
QuotaSampler(plan_of, {"pro": SampleFraction(0.5)}).sample(users)
```

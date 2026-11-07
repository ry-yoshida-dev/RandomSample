# sampler

## Overview

Sampling algorithms. Every sampler derives from `Sampler[T]`, takes all settings in its constructor, and returns a `SampleResult[T]` from `sample(population)`. Stratified samplers return a `StratifiedSampleResult` with the per-stratum breakdown.

## Components

| Component | Responsibility |
| --- | --- |
| [base.py](base.py) | Abstract base class shared by every sampler. |
| [samplers/](samplers/README.md) | Concrete `Sampler` subclasses. |
| [stratum_allocator.py](stratum_allocator.py) | Splits a total into per-stratum counts. |
| [allocation_strategy.py](allocation_strategy.py) | `PROPORTIONAL` / `EQUAL` allocation rules. |

## Examples

```python
from array_sampling import (
    BernoulliSampler,
    QuotaSampler,
    SampleCount,
    SampleFraction,
    StratifiedSampler,
)

one_percent = BernoulliSampler[int](0.01).stream(range(10**9))


def plan_of(user: tuple[int, str]) -> str:
    return user[1]


users = [(1, "free"), (2, "pro")]
StratifiedSampler(plan_of, SampleCount(2), minimum_per_stratum=1).sample(users)
QuotaSampler(plan_of, {"pro": SampleFraction(0.5)}).sample(users)
```

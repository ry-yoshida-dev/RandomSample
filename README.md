# array-sampling

## Overview

Dependency-free sampling utilities for arrays and streams: uniform or weighted sampling with or without replacement, index-only sampling of lazy arrays, single-pass reservoir and Bernoulli sampling, and stratified sampling with allocation strategies and quotas. Every sampler derives from `Sampler[T]`, is configured in its constructor, and returns a `SampleResult[T]` from `sample(population)`, so samplers are interchangeable.

| Situation | Sampler | Memory |
| --- | --- | --- |
| Array in memory or lazily indexable | `ArraySampler` | `O(k)` uniform, `O(n)` weighted |
| Stream, fixed sample size | `ReservoirSampler` | `O(k)` |
| Stream, fixed size, weighted | `WeightedReservoirSampler` | `O(k)` |
| Stream, fixed rate | `BernoulliSampler` | `O(1)` with `stream` |
| Groups must be represented | `StratifiedSampler` | `O(n)` indices |
| Explicit size per group | `QuotaSampler` | `O(n)` indices |
| Many small index samples at once (NumPy) | `array_sampling.batch.BatchIndexSampler` | `O(Bk)` |

## Installation

Requires Python 3.12+.

```bash
pip install .
pip install ".[numpy]"  # for array_sampling.batch
```

## Usage

```python
from array_sampling import (
    ArraySampler,
    RandomGenerator,
    ReplacementMode,
    ReservoirSampler,
    SampleCount,
    SampleFraction,
    StratifiedSampler,
)

random_generator = RandomGenerator.from_seed(42)

ArraySampler(SampleCount(10), random_generator=random_generator).sample(range(1_000))

weights = {"a": 5.0, "b": 1.0, "c": 1.0}
ArraySampler(SampleCount(2), weight_of=weights.__getitem__).sample(["a", "b", "c"])

ArraySampler(SampleFraction(1.0), replacement=ReplacementMode.SWR).sample(["a", "b", "c"])

ReservoirSampler(100, random_generator).sample(range(10_000_000)).items

records = [("free", 1), ("free", 2), ("pro", 3), ("pro", 4)]
StratifiedSampler(lambda record: record[0], SampleCount(2)).sample(records)
```

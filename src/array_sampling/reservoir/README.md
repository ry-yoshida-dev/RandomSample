# reservoir

## Overview

Reservoir sampling keeps a uniform (or weighted) sample of fixed size `k`
from a stream whose length is unknown, reading each element once and holding
only `k` elements in memory. The reservoir is the fixed-size container of the
current candidates: every new element may replace one of them, and the final
contents are a valid sample of everything seen.

The classes here are stateful and push-based: feed elements with `add` or
`extend` as they arrive and read the current sample with `result` at any
time. For a single pass over an iterable, use `ReservoirSampler` or
`WeightedReservoirSampler` from `array_sampling.sampler`, which wrap them.

## Components

| Component | Responsibility |
| --- | --- |
| [uniform.py](uniform.py) | `UniformReservoir`: uniform reservoir using Li's Algorithm L, which skips elements instead of drawing per element. |
| [weighted.py](weighted.py) | `WeightedReservoir`: weighted reservoir without replacement (Efraimidis-Spirakis A-Res, Gumbel-form keys in a top-k heap). |

## Examples

```python
from array_sampling import RandomGenerator, UniformReservoir, WeightedReservoir

reservoir: UniformReservoir[str] = UniformReservoir(100, RandomGenerator.from_seed(42))
with open("access.log") as lines:
    reservoir.extend(lines)
reservoir.result().items

weighted: WeightedReservoir[str] = WeightedReservoir(2)
weighted.add("rare", 1.0)
weighted.add("common", 10.0)
weighted.result().items
```

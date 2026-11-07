# reservoir

## Overview

Stateful, push-based reservoirs that keep a fixed-size sample of a stream of unknown length: feed elements with `add` or `extend` and read the current sample with `result` at any time. For a single pass over an iterable, use `ReservoirSampler` or `WeightedReservoirSampler` from [sampler/](../sampler/README.md).

## Components

| Component | Responsibility |
| --- | --- |
| [uniform.py](uniform.py) | `UniformReservoir`: uniform reservoir (Algorithm L). |
| [weighted.py](weighted.py) | `WeightedReservoir`: weighted reservoir without replacement (A-Res). |

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

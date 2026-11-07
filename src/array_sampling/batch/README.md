# batch

## Overview

Vectorised NumPy sampling for workloads that need many small samples at once, such as minimal subsets for RANSAC-style hypothesis generation. Requires the `numpy` extra, so it is not re-exported from `array_sampling`.

## Components

| Component | Responsibility |
| --- | --- |
| [index_sampler.py](index_sampler.py) | Batched uniform index sampling without replacement. |
| [batch_strategy.py](batch_strategy.py) | Automatic, vectorised, or per-row drawing strategy. |

## Examples

```python
import numpy as np

from array_sampling.batch import BatchIndexSampler

sampler = BatchIndexSampler(np.random.default_rng(42))
sampler.sample(np.full(1_000, 50, dtype=np.intp), 4)
```

# batch

## Overview

Vectorised NumPy sampling for workloads that need many small samples at once,
such as minimal subsets for RANSAC-style hypothesis generation. Requires the
`numpy` extra (`pip install "array-sampling[numpy]"`); the rest of the library
stays dependency-free, so this package is not re-exported from
`array_sampling`.

`BatchIndexSampler` draws `B` samples of `k` distinct indices, uniformly over
subsets, with a population size per row. `BatchStrategy.VECTORISED` runs `k`
NumPy steps, about `k²` NumPy calls over `B` elements each, so it wins for
large batches with small `k`. `BatchStrategy.PER_ROW` calls `Generator.choice`
once per row, which wins for small batches or large `k`. The default,
`BatchStrategy.AUTOMATIC`, picks between them per call from a running-time
estimate based on both `B` and `k`.

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

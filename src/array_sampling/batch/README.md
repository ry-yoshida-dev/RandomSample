# batch

## Overview

Vectorised NumPy sampling for workloads that need many small samples at once,
such as minimal subsets for RANSAC-style hypothesis generation. Requires the
`numpy` extra (`pip install "array-sampling[numpy]"`); the rest of the library
stays dependency-free, so this package is not re-exported from
`array_sampling`.

`BatchIndexSampler` draws `B` samples of `k` distinct indices, uniformly over
subsets, with a population size per row. For `k <= max_vectorised_count`
(default 32) it runs `k` vectorised steps costing `O(B·k²)` in total; above
that it calls `Generator.choice` once per row (`O(B·k)` plus Python overhead
per row), which is faster for large `k`.

## Components

| Component | Responsibility |
| --- | --- |
| [index_sampler.py](index_sampler.py) | Batched uniform index sampling without replacement. |
| [batch_strategy.py](batch_strategy.py) | Vectorised versus per-row drawing strategy. |

## Examples

```python
import numpy as np

from array_sampling.batch import BatchIndexSampler

sampler = BatchIndexSampler(np.random.default_rng(42))
sampler.sample(np.full(1_000, 50, dtype=np.intp), 4)
```

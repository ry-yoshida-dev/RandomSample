# array_sampling

## Overview

Public package. Every public name is importable from `array_sampling`, except `batch`, which needs the `numpy` extra and is imported from `array_sampling.batch`.

## Components

| Component | Responsibility |
| --- | --- |
| [sampler/](sampler/README.md) | Array, streaming, and stratified sampling algorithms. |
| [reservoir/](reservoir/README.md) | Incremental fixed-size reservoirs fed one element at a time. |
| [sizing/](sizing/README.md) | Sample size specifications and rounding of fractional counts. |
| [exceptions/](exceptions/README.md) | Exception hierarchy rooted at `SamplingError`. |
| [batch/](batch/README.md) | Vectorised NumPy batch sampling (optional `numpy` extra). |
| [internal/](internal/README.md) | Implementation details: index drawing, strata, and weight validation. |
| [random_access_array.py](random_access_array.py) | Protocol for `len` + integer indexing + iteration, enabling lazy large arrays. |
| [random_generator.py](random_generator.py) | Seedable random number generator and overflow-safe weighted keys. |
| [replacement_mode.py](replacement_mode.py) | With / without replacement switch. |
| [sample_result.py](sample_result.py) | Selected items aligned with their source positions. |
| [stratified_sample_result.py](stratified_sample_result.py) | `SampleResult` with a per-stratum breakdown. |

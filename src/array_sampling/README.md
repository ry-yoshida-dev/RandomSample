# array_sampling

## Overview

Public package. Everyday names are importable from `array_sampling`:
samplers, sample sizes (`SampleCount`, `SampleFraction`), `RandomGenerator`,
`ReplacementMode`, `SampleResult`, `StratifiedSampleResult`, and exceptions. Less common names live in
their subpackages.

## Components

| Component | Responsibility |
| --- | --- |
| [sampler/](sampler/README.md) | Array, streaming, and stratified sampling algorithms. |
| [reservoir/](reservoir/README.md) | Incremental fixed-size reservoirs fed one element at a time. |
| [sizing/](sizing/README.md) | Sample size specifications and rounding of fractional counts. |
| [exceptions/](exceptions/README.md) | Exception hierarchy rooted at `SamplingError`. |
| [internal/](internal/README.md) | Low-level helpers: array protocol, index drawing, strata, and weight validation. |
| [random_generator.py](random_generator.py) | Seedable random number generator and log-space weighted keys. |
| [replacement_mode.py](replacement_mode.py) | With / without replacement switch. |
| [sample_result.py](sample_result.py) | Selected items aligned with their source positions. |
| [stratified_sample_result.py](stratified_sample_result.py) | `SampleResult` with a per-stratum breakdown. |

## Examples

```python
from array_sampling import ArraySampler, RandomGenerator, SampleCount

sampler: ArraySampler[int] = ArraySampler(
    SampleCount(10), random_generator=RandomGenerator.from_seed(42)
)
sampler.sample(range(1_000))
```

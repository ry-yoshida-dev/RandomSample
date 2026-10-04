# sizing

## Overview

Specifications of how many elements a sampler draws. `SampleCount` and
`SampleFraction` are re-exported from `array_sampling`; import `SampleSize`
from `array_sampling.sizing` and `RoundingMode` from
`array_sampling.sizing.utils`.

## Components

| Component | Responsibility |
| --- | --- |
| [sample_size.py](sample_size.py) | Abstract specification of how many elements to draw. |
| [sample_count.py](sample_count.py) | Absolute element count. |
| [sample_fraction.py](sample_fraction.py) | Ratio of the population with exact decimal rounding. |
| [utils/](utils/README.md) | Supporting options such as rounding of fractional counts. |

## Examples

```python
from array_sampling import SampleCount, SampleFraction
from array_sampling.sizing.utils import RoundingMode

SampleCount(10).resolve(1_000)  # 10
SampleFraction(0.1, RoundingMode.CEIL).resolve(30)  # 3 (exact decimal arithmetic)
```

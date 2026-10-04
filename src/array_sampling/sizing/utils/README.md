# utils

## Overview

Supporting options for the sample size specifications in the parent package.

## Components

| Component | Responsibility |
| --- | --- |
| [rounding_mode.py](rounding_mode.py) | `FLOOR` / `CEIL` / `NEAREST` rounding of fractional counts. |

## Examples

```python
from array_sampling import SampleFraction
from array_sampling.sizing.utils import RoundingMode

SampleFraction(0.1, RoundingMode.CEIL).resolve(30)  # 3
```

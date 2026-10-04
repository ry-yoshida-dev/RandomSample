# internal

## Overview

Low-level helpers used by the samplers. Typical callers never need them:
`RandomAccessArray` only matters when annotating custom lazy containers, and
the other components are implementation details.

## Components

| Component | Responsibility |
| --- | --- |
| [random_access_array.py](random_access_array.py) | Protocol for `len` + integer indexing + iteration, enabling lazy large arrays. |
| [index_drawer.py](index_drawer.py) | Uniform and weighted index drawing with or without replacement. |
| [strata.py](strata.py) | Groups population indices by stratum and draws per-stratum samples. |
| [weight_validator.py](weight_validator.py) | Fail-fast validation of weights. |

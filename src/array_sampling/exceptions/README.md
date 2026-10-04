# exceptions

## Overview

Exception hierarchy of the library. Every error derives from `SamplingError`,
which itself derives from `ValueError`, so callers can catch either the
library-specific base class or the built-in exception.

```text
ValueError
└── SamplingError
    ├── InvalidSampleSizeError
    ├── InvalidWeightError
    ├── InsufficientPopulationError  (exposes .requested / .available)
    └── UnknownStratumError          (exposes .strata)
```

## Components

| Component | Responsibility |
| --- | --- |
| [sampling_error.py](sampling_error.py) | Base class of all library exceptions. |
| [invalid_sample_size_error.py](invalid_sample_size_error.py) | Invalid count, fraction, capacity, or probability. |
| [invalid_weight_error.py](invalid_weight_error.py) | Negative or non-finite weights. |
| [insufficient_population_error.py](insufficient_population_error.py) | Population too small for the requested sample. |
| [unknown_stratum_error.py](unknown_stratum_error.py) | Quota for a stratum absent from the population. |

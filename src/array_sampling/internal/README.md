# internal

## Overview

Low-level helpers used by the samplers. Not part of the public API.

## Components

| Component | Responsibility |
| --- | --- |
| [index_drawer.py](index_drawer.py) | Uniform and weighted index drawing with or without replacement. |
| [strata.py](strata.py) | Groups population indices by stratum and draws per-stratum samples. |
| [weight_validator.py](weight_validator.py) | Fail-fast validation of weights. |

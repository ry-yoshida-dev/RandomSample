# samplers

## Overview

Concrete implementations of `Sampler[T]`.

## Components

| Component | Responsibility |
| --- | --- |
| [array.py](array.py) | Uniform and weighted sampling with or without replacement. |
| [reservoir.py](reservoir.py) | Single-pass uniform fixed-size sampling. |
| [weighted_reservoir.py](weighted_reservoir.py) | Single-pass weighted fixed-size sampling. |
| [bernoulli.py](bernoulli.py) | Rate-based sampling with geometric skips. |
| [stratified.py](stratified.py) | Splits a total across strata and samples each one. |
| [quota.py](quota.py) | Samples an explicit quota from each stratum. |

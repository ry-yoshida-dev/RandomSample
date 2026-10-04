# samplers

## Overview

Concrete implementations of `Sampler[T]`. Each one is configured through its
constructor and draws with `sample(population)`, so they are interchangeable
wherever a `Sampler[T]` is expected. See the [parent README](../README.md) for
the algorithms and their complexity.

## Components

| Component | Responsibility |
| --- | --- |
| [array.py](array.py) | Uniform and weighted sampling with or without replacement. |
| [reservoir.py](reservoir.py) | Single-pass uniform fixed-size sampling. |
| [weighted_reservoir.py](weighted_reservoir.py) | Single-pass weighted fixed-size sampling. |
| [bernoulli.py](bernoulli.py) | Rate-based sampling with geometric skips. |
| [stratified.py](stratified.py) | Splits a total across strata and samples each one. |
| [quota.py](quota.py) | Samples an explicit quota from each stratum. |

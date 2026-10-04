# tests

## Overview

Pytest suite covering deterministic behaviour (seeded), statistical sanity
checks with loose tolerances, and fail-fast error handling.

## Components

| Component | Responsibility |
| --- | --- |
| [test_sampler.py](test_sampler.py) | Every sampler honours the shared `Sampler` contract. |
| [test_sample_size.py](test_sample_size.py) | Count / fraction resolution and validation. |
| [test_array_sampler.py](test_array_sampler.py) | Uniform and weighted array sampling. |
| [test_reservoir.py](test_reservoir.py) | Algorithm L reservoir and its sampler. |
| [test_weighted_reservoir.py](test_weighted_reservoir.py) | Weighted reservoir and its sampler. |
| [test_bernoulli_sampler.py](test_bernoulli_sampler.py) | Rate-based sampling, eager and lazy. |
| [test_stratum_allocator.py](test_stratum_allocator.py) | Allocation rounding, capping, and minimums. |
| [test_stratified_sampler.py](test_stratified_sampler.py) | Stratified and quota sampling. |

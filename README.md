# SNEWS Data Formats

This package contains common data models and utilities for standardizing data formats across SNEWS packages.

## Features

- Data models for key SNEWS data types like messages and timestamps with validation via Pydantic
- Message models for different tiers like heartbeat, retraction, timing, significance, and coincidence
- Utilities for handling nanosecond timestamps and leap seconds
- Static data for supported detectors
- Generation of JSON schemas for data models
- Comprehensive testing suite

## Getting Started

If you don't have [poetry](https://python-poetry.org/docs/#installing-with-the-official-installer), install that first.

Install the package:
```bash
poetry install
```

Use it in your code:
```python
from snews.models.messages import SignificanceTierMessage

message = SignificanceTierMessage(
    detector_name="Super-K",
    p_values: [0.43, 0.32, 0.01],
    t_bin_width_sec: 5e-3
)

print(message.model_dump())
```

See the [documentation](docs/index.md) for more details on the available data models and utilities.

See `snews/examples` for ipython notebooks.

## Contributing
Contributions are welcome!

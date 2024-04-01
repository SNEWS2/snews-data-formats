# -*- coding: utf-8 -*-
__all__ = [
    "PrecisionTimestamp"
]

# Standard library imports
from datetime import UTC, datetime
from typing import Literal, Optional, Union

# Third party imports
import numpy as np
from pydantic import BaseModel, Field, field_validator

# Local imports
from ..data.utilities import num_leap_seconds_between


# .................................................................................................
class PrecisionTimestamp(BaseModel, arbitrary_types_allowed=True):
    """A timestamp with up to nanosecond precision

    This class is a wrapper around the `numpy.datetime64` class. It provides a convenient way to
    convert between different timestamp formats and to perform arithmetic operations on timestamps
    with different precisions, while accounting for leap seconds.

    Args:
        timestamp (optional): Timestamp input. Defaults to current UTC time.
            Supported datatypes: `numpy.datetime64`, `datetime`, `str`.
        precision (optional): Precision on the number of seconds. Defaults to "ns".
            Supported values: "s", "ms", "us", "ns".
    """

    class Config:
        validate_assignment = True

    timestamp: Optional[Union[np.datetime64, datetime, str]] = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp input",
        validate_default=True
    )

    precision: Optional[Literal["s", "ms", "us", "ns"]] = Field(
        default="ns",
        description="Precision on the number of seconds",
        validate_default=True
    )

    def to_string(self):
        return np.datetime_as_string(
            self.timestamp,
            unit=self.precision,
            timezone="UTC"
        )

    def to_numpy(self):
        return self.timestamp

    def to_datetime(self):
        timestamp_str = self.to_string()
        return datetime.fromisoformat(timestamp_str)

    @field_validator("timestamp")
    def _validate_and_cast_timestamp(cls, v):
        if not isinstance(v, np.datetime64):
            v = np.datetime64(v)
            return v

        if isinstance(v, np.datetime64):
            return v

    def __sub__(self, other) -> np.timedelta64:
        if isinstance(other, PrecisionTimestamp):
            timedelta = (self.timestamp - other.timestamp)
            leap_seconds = np.timedelta64(
                num_leap_seconds_between(self.timestamp, other.timestamp),
                "s"
            )

            return timedelta + leap_seconds

        else:
            raise TypeError("Unsupported operand type(s) for -: 'PrecisionTimestamp' and " +
                            type(other).__name__)

    def __str__(self):
        return self.to_string()

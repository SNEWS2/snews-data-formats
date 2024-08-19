import datetime

import numpy as np
import pytest

from snews.data.utilities import num_leap_seconds_between
from snews.models.timing import PrecisionTimestamp


def test_precision_timestamp_input_string():
    assert PrecisionTimestamp(timestamp="2023-12-31T12:34:56.123456")


def test_precision_timestamp_input_datetime():
    assert PrecisionTimestamp(timestamp=datetime.datetime(2020, 1, 1))


def test_precision_timestamp_input_numpy():
    assert PrecisionTimestamp(timestamp=np.datetime64("2023-12-31T12:34:56.123456"))


def test_count_number_leap_seconds_between_times():
    t1 = PrecisionTimestamp(timestamp="2016-12-31T23:59:59Z")
    t2 = PrecisionTimestamp(timestamp="2017-01-01T00:00:00Z")
    t3 = PrecisionTimestamp(timestamp="2017-01-01T00:00:01Z")

    assert num_leap_seconds_between(t1.to_numpy(), t2.to_numpy()) == 1
    assert num_leap_seconds_between(t2.to_numpy(), t3.to_numpy()) == 0


def test_precision_timestamp_subtract():
    t1 = PrecisionTimestamp(timestamp="2017-01-01T00:00:00Z")
    t2 = PrecisionTimestamp(timestamp="2017-01-01T00:00:01Z")

    assert t2 - t1 == np.timedelta64(1, 's')


def test_precision_timestamp_str_output():
    t = PrecisionTimestamp(timestamp="2016-12-31T23:59:59Z")
    assert str(t) == "2016-12-31T23:59:59.000000000Z"


def test_precision_timestamp_datetime_output():
    t = PrecisionTimestamp(timestamp="2016-12-31T23:59:59Z")
    assert t.to_datetime() == datetime.datetime(
        2016, 12, 31, 23, 59, 59,
        tzinfo=datetime.timezone.utc
    )


def test_precision_timestamp_tzinfo_conversion():
    timestamp = datetime.datetime(
        1987, 2, 24, 5, 31, 00,
        tzinfo=datetime.timezone(datetime.timedelta(hours=-5), 'EST')
    )

    t = PrecisionTimestamp(timestamp=timestamp, precision="s")

    t_datetime = t.to_datetime()
    t_string = t.to_string()

    assert t_datetime == timestamp.astimezone(datetime.UTC) and t_string == "1987-02-24T10:31:00Z"


def test_precision_timestamp_incompatible_subtraction():
    with pytest.raises(TypeError) as exc_info:
        PrecisionTimestamp(timestamp="1987-02-24T05:31:00Z") - 1

    assert "Unsupported operand type(s)" in str(exc_info.value)

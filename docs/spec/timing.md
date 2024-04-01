---
title: SNEWS Data Specification — Timing
summary: Specification for SNEWS timestamps.
---

# SNEWS Data Specification <br> Timing


## Introduction

Accurate and precise timestamps are a critical component of the SNEWS system. Timestamps are used in messages that SNEWS receives and sends. They are also used internally to determine coincidence between multiple detectors. To ensure that timestamps are consistent across the SNEWS network, the following specification is used.

### SNEWS Timestamps

SNEWS timestamps are broadly divided into two categories:

1. **Scientific timestamps** <br>Used primarily for neutrino detection events. They are used to determine the time of a neutrino interaction in a detector. Other quantities may also be considered scientific timestamps if they require a certain level of precision to be useful for the SNEWS mission.
2. **Coarse timestamps** <br>Used for all other purposes where a particular level of precision is not required. This might include miscellaneous log messages, detector status updates, and other messages that are not directly related to neutrino detection events. For the most part, coarse timestamps are used for human-readable messages.

### Leap Seconds

The detection of coincident neutrinos is deteremined by comparing the timestamps of neutrino events from multiple detectors. If a leap second is introduced between two timestamps, then the difference between the two timestamps will be off by one second, which could cause a lead to a supernova alert being delayed or missed entirely.

To avoid this, any difference between two scientific timestamps must take into account the number of leap seconds that have occurred between the two timestamps.

---

## Requirements

1. A common time standard must be used across the SNEWS network.
2. Scientific timestamps must have nanosecond precision.
3. All timestamps must be in UTC.
4. Differences between scientific timestamps must take into account leap seconds.

---

## Specification

- SNEWS uses the [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) standard for all timestamps.
- Scientific timestamps follow the format `YYYY-MM-DDTHH:MM:SS.sssssssssZ`.

---

## Implementation
SNEWS Data Format uses the [NumPy datetime64](https://docs.scipy.org/doc/numpy/reference/arrays.datetime.html) type to represent timestamps, a 64-bit integer that represents the number of nanoseconds since the Unix epoch (1970-01-01T00:00:00Z).

This type is used because it is a standard type that is supported by many programming languages and libraries. It is also used because it is a fixed-width type that is easy to serialize and deserialize.

SNEWS Data Formats provides a `PrecisionTimestamp` data class that allows the user to cast a timestamp to a particular precision, regardless of the precision of the underlying timestamp. The default precision is nanoseconds, but the user can cast to seconds, milliseconds, or microseconds.

### Data Model: Precision Timestamp

| Name | Type | Description | Constraints |
| ---- | ---- | ----------- | ----------- |
| `timestamp` | `np.datetime64`, <br> `datetime`, or <br> String | Timestamp input | |
| `precision` | String | Precision of timestamp | One of: `s`, `ms`, `us`, `ns` |

#### Example Usage

```python
from snews.models.timing import PrecisionTimestamp

# Create a timestamp with nanosecond precision
ts = PrecisionTimestamp("2018-07-10T12:00:00.123456789Z")
print(ts)
# 2018-07-10T12:00:00.123456789Z
ts = PrecisionTimestamp("2018-07-10T12:00:00.123")
print(ts)
# 2018-07-10T12:00:00.123000000Z

# Create a timestamp with second precision
ts = PrecisionTimestamp("2018-07-10T12:00:00.123456789Z", precision="s")
print(ts)
# 2018-07-10T12:00:00Z

# Create a timestamp with millisecond precision
ts = PrecisionTimestamp("2018-07-10T12:00:00.123456789Z", precision="ms")
print(ts)
# 2018-07-10T12:00:00.123Z
```

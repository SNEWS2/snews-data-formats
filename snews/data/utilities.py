# -*- coding: utf-8 -*-

# Standard library imports
from typing import Any, Optional

# Third party imports
import numpy as np
from pydantic import BaseModel

# Local imports
from .timing import leap_seconds


# .................................................................................................
def query(data: list, query: Any) -> Optional[list]:
    """
    Query a list of values, dicts, or Pydantic models

    The query can be a single value or a dict of key-value pairs. If the query is a dict, then the
    function returns a list of all values that match the key-value pairs in the query. If the query
    is a single value, then the function returns a list of all values that match that key.

    Parameters
    ----------
    data : list
        List of values, dicts, or Pydantic models
    query : Any
        Query to match against data, either a single value or a dict of key-value pairs

    Returns
    -------
    result : list
        List of values that match the query

    Examples
    --------
    Query a list of dicts
    >>> data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    >>> query(data, {"a": 1})
    [{"a": 1, "b": 2}]

    Query a list of Pydantic models
    >>> class Foo(BaseModel):
    ...     a: int
    ...     b: int
    >>> data = [Foo(a=1, b=2), Foo(a=3, b=4)]
    >>> query(data, {"a": 1})
    [Foo(a=1, b=2)]

    Query a list of values
    >>> data = [1, 2, 3, 4]
    >>> query(data, 1)
    [1]
    """

    result: Optional[list] = None

    # Case A: data is a list of dicts and query is a dict
    if isinstance(data[0], dict) and isinstance(query, dict):
        result = [i for i in data if all(i.get(k) == v for k, v in query.items())]

    # Case B: data is a list of dicts and query is a single value
    if isinstance(data[0], dict) and not isinstance(query, dict):
        result = [d[query] for d in data if query in d.keys()]

    # Case C: data is a list of Pydantic models and query is a dict
    if isinstance(data[0], BaseModel) and isinstance(query, dict):
        result = [i for i in data if all(i.model_dump().get(k) == v for k, v in query.items())]

    # Case D: data is a list of Pydantic models and query is a single value
    if isinstance(data[0], BaseModel) and not isinstance(query, dict):
        result = [i.model_dump().get(query) for i in data if query in i.model_dump().keys()]

    # Case E: data is a simple list (of non-iterable objects) and query is a single value
    if isinstance(data[0], (int, float, str)) and not isinstance(query, dict):
        result = [i for i in data if i == query]

    return result


# .................................................................................................
def num_leap_seconds_between(date1: np.datetime64, date2: np.datetime64) -> int:
    """
    Count the number of leap seconds between two timestamps.

    Note: Dates can be in any order.

    Parameters
    ----------
    date1 : np.datetime64
        First timestamp

    date2 : np.datetime64
        Second timestamp

    Returns
    -------
    num_leap_seconds : int
        Number of leap seconds between self and other timestamps

    Examples
    --------
    >>> import numpy as np
    >>> from snews.data import num_leap_seconds_between
    >>> date1 = np.datetime64("2015-12-31T23:59:59")
    >>> date2 = np.datetime64("2016-01-01T00:00:00")
    >>> num_leap_seconds_between(date1, date2)
    1

    """
    start, end = sorted([date1, date2])

    boundaries_crossed = [b for b in leap_seconds if start <= b < end]

    return len(boundaries_crossed)

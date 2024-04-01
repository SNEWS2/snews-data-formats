# -*- coding: utf-8 -*-
from snews.data import detectors, mock, timing
from snews.data.utilities import query


def test_data_import():
    if not detectors:
        raise AssertionError("No detector data loaded")
    if not mock:
        raise AssertionError("No mock data loaded")
    if not timing:
        raise AssertionError("No timing data loaded")
    assert True


def test_data_query_case_A():
    # Case A: data is a list of dicts and query is a dict
    data = [
        {"a": 1, "b": 2, "c": 3},
        {"a": 1, "b": 4, "e": 5}
    ]
    selector1 = {"a": 1}
    result1 = data
    selector2 = {"b": 2}
    result2 = [{"a": 1, "b": 2, "c": 3}]

    # Case 1: Query a list of dicts for a single key-value pair
    assert query(data, selector1) == result1
    assert query(data, selector2) == result2


def test_data_query_case_B():
    # Case B: data is a list of dicts and query is a single value
    data = [
        {"a": 1, "b": 2, "c": 3},
        {"a": 1, "b": 4, "e": 5}
    ]
    selector = "b"
    result = [2, 4]

    assert query(data, selector) == result


def test_data_query_case_C():
    # Case C: data is a list of Pydantic models and query is a dict

    data = detectors.all
    selector = {"name": "Super-K"}
    result = [detector for detector in detectors.all if detector.name == "Super-K"]

    assert query(data, selector) == result


def test_data_query_case_D():
    # Case D: data is a list of Pydantic models and query is a single value

    data = detectors.all
    selector = "name"
    result = detectors.names

    assert query(data, selector) == result


def test_data_query_case_E():
    # Case E: data is a simple list (of non-iterable objects) and query is a single value

    data = [1, 2, 3, 4]
    selector = 1
    result = [1]

    assert query(data, selector) == result


def test_detector_comparison():
    # Detectors are the same
    detectorA = detectors.all[0]
    detectorB = detectorA.copy(deep=True)
    assert detectorA == detectorB

    # Detectors have a different name
    detectorA.name = "Super-K"
    detectorB.name = "Hyper-K"
    assert detectorA != detectorB

    # Detectors have a different id
    detectorA.id = 1
    detectorA.id = 2
    detectorB.name = "Super-K"
    assert detectorA != detectorB

    # One variable is not Detector type
    assert detectorA != "Detector B"

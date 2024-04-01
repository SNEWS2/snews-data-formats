# -*- coding: utf-8 -*-

# Standard library imports
from importlib import resources

# Local imports
from ..io import read_json_file

# Module exports
__all__ = [
    "coincidence_scenarios",
    "time_formats",
]


data_directory = resources.files("snews.data.mock")

# Load Mock Data
coincidence_scenarios = read_json_file(data_directory / "coincidence_scenarios.json")
time_formats = read_json_file(data_directory / "time_formats.json")

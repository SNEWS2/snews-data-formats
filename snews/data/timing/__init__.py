# -*- coding: utf-8 -*-

# Standard library imports
from importlib import resources

# Third party imports
import numpy as np

# Local imports
from ..io import read_json_file

# Module exports
__all__ = [
    "leap_seconds",
]

data_directory = resources.files("snews.data.timing")

# Load leap second data
leap_second_filepath = data_directory / "leap_seconds.json"
leap_seconds = [
    np.datetime64(date + "T23:59:59") for date in read_json_file(leap_second_filepath)
]

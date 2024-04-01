# -*- coding: utf-8 -*-

# Standard library imports
from importlib import resources

# Local imports
from ...models.detectors import Detector
from ..io import read_json_file

# Module exports
__all__ = [
    "all",
    "names",
]

data_directory = resources.files("snews.data.detectors")

# Load Detector Data
detector_filepaths = list(data_directory.glob("*.json"))

all = [Detector(**read_json_file(f)) for f in detector_filepaths]
names = [d.name for d in all]

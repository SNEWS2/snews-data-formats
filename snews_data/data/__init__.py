# -*- coding: utf-8 -*-
"""SNEWS Data Services - Data

This module provides an interface to static data contained in JSON files in the ``data`` directory.

The data registry (`SNEWSDataRegistry`) is responsible for importing the JSON files and storing the
data in memory based on a label-model mapping. The label corresponds to the base name of the JSON
file and the model is the Pydantic model used to validate those data.

Interfaces for specific data types are provided (e.g., the `SNEWSDetectorData` class) to provide
convenience methods for accessing the data.

Todo:
    * Make the Data Registry a singleton?
"""

# Standard library modules
import json
from pathlib import Path

# Local modules
from .. import models


# .................................................................................................
class SNEWSDataRegistry:
    """Registry for imported SNEWS data"""
    def __init__(self):
        self.data_path = Path(__file__).parent
        self.data = dict()
        self.model_labels = {
            "detectors": models.detectors.DetectorModel,
            # "test_scenarios": "TestScenarioModel",
        }
        self._import_files()

    def _import_files(self):
        """Import JSON files into registry"""
        for model_label, model in self.model_labels.items():
            with open(f"{self.data_path}/{model_label}.json", "r") as f:
                self.data[model_label] = [model(**i) for i in json.load(f)]

    def get_data(self, model_label: str = None):
        if model_label is None:
            return self.data

        if model_label not in self.data:
            raise KeyError

        return self.data.get(model_label)


# .................................................................................................
class SNEWSDetectorData():
    def __init__(self, registry: SNEWSDataRegistry = SNEWSDataRegistry(), model_label="detectors"):
        self.registry = registry
        self.model_label = model_label
        self.data = registry.get_data(model_label=model_label)

        self.names = [detector.name for detector in self.data]

    def get_by_name(self, name):
        if name not in self.names:
            raise KeyError

        for detector in self.data:
            if detector.name == name:
                return detector


# .................................................................................................

registry = SNEWSDataRegistry()
detectors = SNEWSDetectorData(registry=registry)

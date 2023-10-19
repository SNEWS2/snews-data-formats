# -*- coding: utf-8 -*-

# Standard library modules
import uuid

# Third-party modules
import pytest

# Local modules
from snews_data import data


# .................................................................................................
def test_invalid_detector_name():
    with pytest.raises(KeyError):
        data.detectors.get_by_name(str(uuid.uuid4().hex))


# .................................................................................................
def test_None_model_label_name():
    model_data = data.registry.get_data(model_label=None)
    assert model_data == data.registry.data


# .................................................................................................
def test_invalid_model_label_name():
    with pytest.raises(KeyError):
        data.registry.get_data(str(uuid.uuid4().hex))

# -*- coding: utf-8 -*-

# Local modules
from snews import models


# .................................................................................................
def test_import_all_models():
    models.__all__
    assert True


# .................................................................................................
def test_import_detector_models():
    expected = models.detectors.__all__
    actual = models.detectors.__dir__()
    assert expected == actual

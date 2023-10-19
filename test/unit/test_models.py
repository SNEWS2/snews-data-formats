# -*- coding: utf-8 -*-

# Local modules
from snews_data import models


# .................................................................................................
def test_import_all_models():
    models.all()
    assert True
